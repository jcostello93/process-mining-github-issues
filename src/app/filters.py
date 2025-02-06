import pm4py
import math
import streamlit as st
from datetime import timedelta


def get_attributes_set(log, field):
    try:
        attributes_set = set(pm4py.get_event_attribute_values(log, field).keys())
    except Exception:
        attributes_set = set()

    return attributes_set


def apply(
    log,
):
    log = log.copy()

    # Checkboxes for filtering noisy events
    activities_set = get_attributes_set(log, "concept:name")
    author_associations_set = get_attributes_set(log, "author_association")
    labels_set = get_attributes_set(log, "label")

    # Sidebar Filter Options
    st.sidebar.header("Filters")

    sample_pct = st.sidebar.number_input(
        "Sample %",
        min_value=1,
        max_value=100,
        value=100,
        step=1,
    )

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
        "Filter Endpoints",
        activities_set,
        default=endpoints.intersection(activities_set),
    )

    variants_count = pm4py.statistics.variants.pandas.get.get_variants_count(log)
    top_k = st.sidebar.number_input(
        f"Top Variants (1 - {len(variants_count)})",
        min_value=1,
        max_value=len(variants_count),
        value=len(variants_count),
        step=1,
    )

    # Checkboxes for author association filtering
    author_values = author_associations_set
    selected_authors = st.sidebar.multiselect(
        "Filter Author Association", author_values, default=author_values
    )
    keep_bot_events = st.sidebar.checkbox("Keep bot events", value=True)

    # Checkbox for merged PR filter
    merged_pr = st.sidebar.checkbox("Only keep cases linked to merged PRs", value=False)

    labels = labels_set
    with st.sidebar.expander("Filter Labels", expanded=False):
        selected_labels = st.multiselect("Select Labels to Keep", labels, default={})

    if sample_pct < 100:
        num_cases = math.floor(log["case:concept:name"].nunique() * (sample_pct / 100))
        log = pm4py.sample_cases(log, num_cases=num_cases)

    try:
        log = pm4py.filter_time_range(
            log, str(time_range[0]), str(time_range[1]), mode="traces_contained"
        )
    except Exception:
        print("Could not filter time range")

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

    if not keep_bot_events:
        try:
            log = pm4py.filter_event_attribute_values(
                log,
                "is_bot_author",
                {True},
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter bot events")

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
