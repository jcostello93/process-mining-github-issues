import streamlit as st
import pm4py
import os
from src.data_pipeline.s3 import fetch_file
from src.app import (
    bottleneck_analysis,
    conformance,
    discovery,
    filters,
    organization,
    stats,
    table,
    variants,
)

st.set_page_config(layout="wide")

repos = {"react"}
try:
    print("Setting env vars")
    S3_BUCKET = st.secrets["S3_BUCKET"]
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["AWS_DEFAULT_REGION"]
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET_ACCESS_KEY"]
    print("Done!")
except Exception:
    print("Running locally")
    S3_BUCKET = os.environ.get("S3_BUCKET")
    repos.add("node-red-contrib-node-reddit")


# Sidebar Navigation
st.sidebar.title("Navigation")
repo = st.sidebar.selectbox("Repo:", repos)
page = st.sidebar.radio(
    "Go to:",
    [
        "Stats",
        "Variants",
        "Discovery",
        "Bottleneck",
        "Conformance",
        "Organization",
        "Table",
    ],
)

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


log, msg = load_log(repo)
filtered_log = filters.apply(log, S3_BUCKET)

if page == "Stats":
    stats.show(filtered_log)
elif page == "Variants":
    variants.show(filtered_log)
elif page == "Discovery":
    discovery.show(log, filtered_log)
elif page == "Table":
    table.show(filtered_log)
elif page == "Bottleneck":
    bottleneck_analysis.show(log, filtered_log)
elif page == "Conformance":
    conformance.show(log, filtered_log)
elif page == "Organization":
    organization.show(filtered_log)
