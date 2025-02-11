import streamlit as st
import pm4py
import json
import os
import math
import datetime
from src.data_pipeline.s3 import fetch_file, upload_file

FILTERS_FILE = "filters.json"


def datetime_converter(obj):
    """Convert datetime objects to ISO format for JSON serialization."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj


def datetime_parser(dct):
    """Convert ISO format strings back to datetime objects during JSON deserialization."""
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                dct[key] = datetime.datetime.fromisoformat(value)
            except ValueError:
                pass
    return dct


def load_filters(S3_BUCKET):
    local_file = fetch_file(FILTERS_FILE, S3_BUCKET, FILTERS_FILE)
    if os.path.exists(local_file):
        with open(local_file, "r") as f:
            return json.load(f, object_hook=datetime_parser)
    return {}


def save_filters(filters, S3_BUCKET):
    """Save filters to a JSON file, converting datetime values to strings."""
    with open(FILTERS_FILE, "w") as f:
        json.dump(filters, f, indent=4, default=datetime_converter)
    upload_file(FILTERS_FILE, S3_BUCKET, FILTERS_FILE)


def delete_filter_set(name, S3_BUCKET):
    """Delete a saved filter set."""
    filters = load_filters(S3_BUCKET)
    if name in filters:
        del filters[name]
        save_filters(filters, S3_BUCKET)


def get_attributes_set(log, field):
    try:
        attributes_set = set(pm4py.get_event_attribute_values(log, field).keys())
    except Exception:
        attributes_set = set()

    return attributes_set


def apply(full_log, S3_BUCKET):
    full_log = full_log.copy()
    filtered_log = full_log

    saved_filters = load_filters(S3_BUCKET)

    st.sidebar.header("Filters")

    selected_filter = st.sidebar.selectbox(
        "Load Saved Filter Set", ["Select..."] + list(saved_filters.keys())
    )

    activities_set = get_attributes_set(full_log, "concept:name")
    author_associations_set = get_attributes_set(full_log, "author_association")
    labels_set = get_attributes_set(full_log, "label")

    default_filters = {
        "sample_pct": 100,
        "start_date": full_log["time:timestamp"]
        .min()
        .replace(tzinfo=None)
        .to_pydatetime(),
        "end_date": full_log["time:timestamp"]
        .max()
        .replace(tzinfo=None)
        .to_pydatetime(),
        "selected_events": list(
            activities_set
            - {
                "milestoned",
                "pinned",
                "subscribed",
                "unmilestoned",
                "unpinned",
                "unsubscribed",
            }
        ),
        "selected_endpoints": list(
            {"closed", "completed", "not_planned"}.intersection(activities_set)
        ),
        "top_k": len(pm4py.statistics.variants.pandas.get.get_variants_count(full_log)),
        "selected_authors": list(author_associations_set),
        "keep_bot_events": True,
        "merged_pr": False,
        "bugs": False,
        "feature_requests": False,
        "selected_labels": [],
    }

    # If a saved filter set is selected, override defaults
    if selected_filter != "Select..." and selected_filter in saved_filters:
        current_filters = saved_filters[selected_filter]
    else:
        current_filters = default_filters

    # Sample percentage filter
    sample_pct = st.sidebar.number_input(
        "Sample %",
        min_value=1,
        max_value=100,
        value=current_filters["sample_pct"],
        step=1,
    )

    time_range = st.sidebar.slider(
        "Select Time Range",
        min_value=full_log["time:timestamp"].min().replace(tzinfo=None).to_pydatetime(),
        max_value=full_log["time:timestamp"].max().replace(tzinfo=None).to_pydatetime(),
        value=(current_filters["start_date"], current_filters["end_date"]),
        step=datetime.timedelta(days=1),
    )

    with st.sidebar.expander("Filter Events", expanded=False):
        selected_events = st.multiselect(
            "Select Events to Keep",
            activities_set,
            default=current_filters["selected_events"],
        )

    selected_endpoints = st.sidebar.multiselect(
        "Filter Endpoints",
        activities_set,
        default=current_filters["selected_endpoints"],
    )

    variants_count = pm4py.statistics.variants.pandas.get.get_variants_count(
        filtered_log
    )
    top_k = st.sidebar.number_input(
        f"Top Variants (1 - {len(variants_count)})",
        min_value=1,
        max_value=len(variants_count),
        value=current_filters["top_k"],
        step=1,
    )

    selected_authors = st.sidebar.multiselect(
        "Filter Author Association",
        author_associations_set,
        default=current_filters["selected_authors"],
    )

    keep_bot_events = st.sidebar.checkbox(
        "Keep bot events", value=current_filters["keep_bot_events"]
    )

    merged_pr = st.sidebar.checkbox(
        "Only keep cases linked to merged PRs", value=current_filters["merged_pr"]
    )

    bugs = st.sidebar.checkbox(
        "Only keep titles containing 'bug'", value=current_filters["bugs"]
    )

    feature_requests = st.sidebar.checkbox(
        "Only keep titles containing 'feature request'",
        value=current_filters["feature_requests"],
    )

    with st.sidebar.expander("Filter Labels", expanded=False):
        selected_labels = st.multiselect(
            "Select Labels to Keep",
            labels_set,
            default=current_filters["selected_labels"],
        )

    # Save filter set
    filter_name = st.sidebar.text_input("Save Filter Set As", "")
    if st.sidebar.button("Save Filter Set"):
        if filter_name:
            saved_filters[filter_name] = {
                "sample_pct": sample_pct,
                "start_date": time_range[0],
                "end_date": time_range[1],
                "selected_events": selected_events,
                "selected_endpoints": selected_endpoints,
                "top_k": top_k,
                "selected_authors": selected_authors,
                "keep_bot_events": keep_bot_events,
                "merged_pr": merged_pr,
                "bugs": bugs,
                "feature_requests": feature_requests,
                "selected_labels": selected_labels,
            }
            save_filters(saved_filters, S3_BUCKET)
            st.sidebar.success(f"Filter set '{filter_name}' saved!")
            st.rerun()

    # Delete a saved filter set
    if saved_filters:
        delete_filter = st.sidebar.selectbox(
            "Delete Saved Filter Set", ["Select..."] + list(saved_filters.keys())
        )
        if delete_filter != "Select..." and st.sidebar.button("Delete Filter Set"):
            delete_filter_set(delete_filter, S3_BUCKET)
            st.sidebar.success(f"Deleted filter set: {delete_filter}")
            st.rerun()

    # Apply filters
    if sample_pct < 100:
        num_cases = math.floor(
            full_log["case:concept:name"].nunique() * (sample_pct / 100)
        )
        filtered_log = pm4py.sample_cases(full_log, num_cases=num_cases)

    try:
        filtered_log = pm4py.filter_time_range(
            filtered_log,
            str(time_range[0]),
            str(time_range[1]),
            mode="traces_contained",
        )
    except Exception:
        print("Could not filter time range")

    if selected_events:
        try:
            filtered_log = pm4py.filter_event_attribute_values(
                filtered_log,
                "concept:name",
                (activities_set - set(selected_events)),
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter activities")

    try:
        filtered_log = pm4py.filter_variants_top_k(filtered_log, top_k)
    except Exception:
        print("Could not filter top variants")

    if selected_authors:
        try:
            filtered_log = pm4py.filter_event_attribute_values(
                filtered_log,
                "author_association",
                (author_associations_set - set(selected_authors)),
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter author_association")

    if not keep_bot_events:
        try:
            filtered_log = pm4py.filter_event_attribute_values(
                filtered_log,
                "is_bot_author",
                {True},
                retain=False,
                level="event",
            )
        except Exception:
            print("Could not filter bot events")

    if merged_pr:
        try:
            filtered_log = pm4py.filter_event_attribute_values(
                filtered_log, "has_merged_pr", {True}, retain=True, level="case"
            )
        except Exception:
            print("Could not filter has_merged_pr")

    if bugs:
        try:
            filtered_log = pm4py.filter_trace_attribute_values(
                filtered_log, "case:title_contains_bug", {True}, retain=True
            )
        except Exception:
            print("Could not filter bugs")

    if feature_requests:
        try:
            filtered_log = pm4py.filter_trace_attribute_values(
                filtered_log, "case:title_contains_feature_request", {True}, retain=True
            )
        except Exception:
            print("Could not filter feature_requests")

    if len(selected_labels) > 0:
        try:
            filtered_log = pm4py.filter_event_attribute_values(
                filtered_log, "label", selected_labels, retain=True, level="case"
            )
        except Exception:
            print("Could not filter label")

    if len(selected_endpoints) > 0:
        try:
            filtered_log = pm4py.filter_end_activities(filtered_log, selected_endpoints)
        except Exception:
            print("Could not filter activities")

    return filtered_log
