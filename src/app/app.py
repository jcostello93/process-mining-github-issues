import streamlit as st
import pm4py
import os
from src.data_pipeline.s3 import fetch_file
from src.app import bottleneck_analysis, conformance, discovery, stats, table, variants
from datetime import timedelta
import math

S3_BUCKET = None
IS_STREAMLIT_CLOUD = "STREAMLIT_SERVER_PORT" in os.environ

st.set_page_config(layout="wide")


try:
    print("Setting env vars")
    S3_BUCKET = st.secrets["S3_BUCKET"]
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["AWS_DEFAULT_REGION"]
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET_ACCESS_KEY"]
    print("Done!")
except Exception:
    print("Running locally")
    S3_BUCKET = None


# Sidebar Navigation
st.sidebar.title("Navigation")
repo = st.sidebar.selectbox("Repo:", {"node-red-contrib-node-reddit", "react"})
page = st.sidebar.radio(
    "Go to:", ["Stats", "Variants", "Discovery", "Bottleneck", "Conformance", "Table"]
)

if "log" not in st.session_state:
    st.session_state["log"] = None
if "log_message" not in st.session_state:
    st.session_state["log_message"] = ""


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))


# Function to Fetch & Load Log
@st.cache_data
def load_log(repo):
    if repo == "react":
        owner = "facebook"
    else:
        owner = "jcostello93"
    file_name = f"{owner}_{repo}_event_log.xes"
    print(f"Running load_log for {owner}, {repo}")
    file_path = os.path.join(ROOT_DIR, file_name)  # Store directly in the root folder

    try:
        local_file = fetch_file(file_path, S3_BUCKET, file_name)  # Fetch from S3
        log = pm4py.read_xes(local_file)  # Load event log
        return log, f"✅ Successfully loaded log: {file_name}"
    except Exception as e:
        return None, f"❌ Error loading log: {e}"


# Display Status
if "log_message" in st.session_state:
    st.write(st.session_state["log_message"])


log, msg = load_log(repo)


def get_attributes_set(field):
    try:
        attributes_set = set(pm4py.get_event_attribute_values(log, field).keys())
    except Exception:
        attributes_set = set()

    return attributes_set


# Checkboxes for filtering noisy events
activities_set = get_attributes_set("concept:name")
author_associations_set = get_attributes_set("author_association")
labels_set = get_attributes_set("label")

# Sidebar Filter Options
st.sidebar.header("Filters")

start_date = log["time:timestamp"].min().replace(tzinfo=None).to_pydatetime()
end_date = log["time:timestamp"].max().replace(tzinfo=None).to_pydatetime()
time_range = st.sidebar.slider(
    "Select Time Range",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    step=timedelta(days=1),
)

noisy_events = set(
    [
        "milestoned",
        "pinned",
        "subscribed",
        "unmilestoned",
        "unpinned",
        "unsubscribed",
    ]
)

with st.sidebar.expander("Filter Events", expanded=False):
    selected_events = st.multiselect(
        "Select Events to Keep",
        activities_set,
        default=(activities_set - noisy_events),
    )

# Checkboxes for filtering endpoints
endpoints = {"closed", "completed", "not_planned"}
selected_endpoints = st.sidebar.multiselect(
    "Filter Endpoints", activities_set, default=endpoints.intersection(activities_set)
)


variants_count = pm4py.statistics.variants.pandas.get.get_variants_count(log)
top_k = st.sidebar.number_input(
    f"Top Variants (1 - {len(variants_count)})",
    min_value=1,
    max_value=len(variants_count),
    value=len(variants_count),
    step=1,
)

sample_pct = st.sidebar.number_input(
    "Sample %",
    min_value=1,
    max_value=100,
    value=100,
    step=1,
)


# Checkboxes for author association filtering
author_values = author_associations_set
selected_authors = st.sidebar.multiselect(
    "Filter Author Association", author_values, default=author_values
)

# Checkbox for merged PR filter
merged_pr = st.sidebar.checkbox("Only keep cases linked to merged PRs", value=False)

labels = labels_set
with st.sidebar.expander("Filter Labels", expanded=False):
    selected_labels = st.multiselect("Select Labels to Keep", labels, default={})


def safe_filter(func, log, description, *args, **kwargs):
    try:
        return func(log, *args, **kwargs)
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return log  # Return the unmodified log if filtering fails


# Apply Filters
def apply_filters(log):
    if sample_pct < 100:
        num_cases = math.floor(log["case:concept:name"].nunique() * (sample_pct / 100))
        log = pm4py.sample_cases(log, num_cases=num_cases)

    if len(selected_events) > 0:
        try:
            log = pm4py.filter_event_attribute_values(
                log,
                "concept:name",
                (activities_set - set(selected_events)),
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter activities")

    if len(selected_endpoints) > 0:
        try:
            log = pm4py.filter_end_activities(log, selected_endpoints)
        except Exception:
            print("Could not filter activities")

    try:
        log = pm4py.filter_variants_top_k(log, top_k)
    except Exception:
        print("Could not filter top variants")

    try:
        log = pm4py.filter_time_range(
            log, str(time_range[0]), str(time_range[1]), mode="traces_contained"
        )
    except Exception:
        print("Could not filter time range")

    if len(selected_authors) > 0:
        try:
            log = pm4py.filter_event_attribute_values(
                log,
                "author_association",
                (author_associations_set - set(selected_authors)),
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter author_association")

    if merged_pr:
        try:
            log = pm4py.filter_event_attribute_values(
                log, "has_merged_pr", {True}, retain=True, level="case"
            )
        except Exception:
            print("Could not filter has_merged_pr")

    if len(selected_labels) > 0:
        try:
            log = pm4py.filter_event_attribute_values(
                log, "label", selected_labels, retain=True, level="case"
            )
        except Exception:
            print("Could not filter label")
    return log


filtered_log = apply_filters(log)

if page == "Stats":
    stats.show(filtered_log)
elif page == "Variants":
    variants.show(filtered_log)
elif page == "Discovery":
    discovery.show(filtered_log)
elif page == "Table":
    table.show(filtered_log)
elif page == "Bottleneck":
    bottleneck_analysis.show(filtered_log)
elif page == "Conformance":
    conformance.show(log, filtered_log)
