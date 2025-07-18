import streamlit as st
import pm4py
from pm4py.algo.filtering.dfg.dfg_filtering import filter_dfg_on_activities_percentage
from pm4py.algo.filtering.dfg.dfg_filtering import filter_dfg_on_paths_percentage
from src.app import evaluate, sample_util
import pandas as pd


def show(full_log, filtered_log):
    full_log = full_log.copy()
    st.title("DFG")

    endpoints = {"closed", "not_planned"}
    selected_endpoints = st.multiselect(
        "Filter endpoints",
        sorted(list(endpoints)),
        default=sorted(list(endpoints)),
    )

    if selected_endpoints:
        filtered_log = pm4py.filtering.filter_end_activities(
            filtered_log, selected_endpoints
        )

    # Discover the frequency DFG using activites and paths to filter
    activities = pm4py.get_event_attribute_values(filtered_log, "concept:name")
    frequency_dfg, start_activities, end_activities = pm4py.discover_dfg(filtered_log)

    activities_perc = st.slider(
        "Activities Percentage", min_value=0.0, max_value=1.0, value=0.90, step=0.05
    )
    paths_perc = st.slider(
        "Paths Percentage", min_value=0.0, max_value=1.0, value=0.10, step=0.05
    )

    frequency_dfg, start_activities, end_activities, activities = (
        filter_dfg_on_activities_percentage(
            frequency_dfg, start_activities, end_activities, activities, activities_perc
        )
    )
    frequency_dfg, start_activities, end_activities, activities = (
        filter_dfg_on_paths_percentage(
            frequency_dfg, start_activities, end_activities, activities, paths_perc
        )
    )

    # Discover the performance DFG (does not support activities and paths filtering)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(
        filtered_log
    )

    # Use the frequency DFG to filter the performance DFG
    removal_list = []
    for edge in performance_dfg:
        if edge not in frequency_dfg:
            removal_list.append(edge)

    for edge in removal_list:
        if edge in performance_dfg:
            del performance_dfg[edge]

    pm4py.save_vis_dfg(
        frequency_dfg,
        start_activities,
        end_activities,
        rankdir="TB",
        file_path="frequency_dfg.svg",
        format="svg",
    )
    pm4py.save_vis_performance_dfg(
        performance_dfg,
        start_activities,
        end_activities,
        aggregation_measure="sum",
        rankdir="TB",
        file_path="performance_dfg_sum.svg",
        format="svg",
    )
    pm4py.save_vis_performance_dfg(
        performance_dfg,
        start_activities,
        end_activities,
        aggregation_measure="median",
        rankdir="TB",
        file_path="performance_dfg_median.svg",
        format="svg",
    )

    st.image("frequency_dfg.svg", use_container_width=False)

    col1, col2 = st.columns(2)

    with col1:
        st.image("performance_dfg_sum.svg", use_container_width=False)

    with col2:
        st.image("performance_dfg_median.svg", use_container_width=False)

    sample_log = sample_util.get(full_log)
    if st.button("🐢 Evaluate model (via petri net)"):
        pnet, pim, pfm = pm4py.convert_to_petri_net(
            frequency_dfg, start_activities, end_activities
        )
        evaluate.show(sample_log, pnet, pim, pfm)

    df_performance = pd.DataFrame.from_dict(performance_dfg, orient="index")
    df_performance["median (hours)"] = df_performance["median"] / 60 / 60
    df_performance["sum (years)"] = df_performance["sum"] / 60 / 60 / 24 / 365
    df_frequency = pd.DataFrame.from_dict(
        frequency_dfg, orient="index", columns=["count"]
    )
    df_frequency.index = pd.MultiIndex.from_tuples(df_frequency.index)
    df = df_performance.merge(
        df_frequency, left_index=True, right_index=True, how="left"
    )
    df.drop(columns=["mean", "max", "min", "stdev", "median", "sum"], inplace=True)
    df.sort_values(by="count", ascending=False, inplace=True)

    df.reset_index(inplace=True)
    df.rename(columns={"level_0": "Source", "level_1": "Target"}, inplace=True)

    st.title("DFG transition aggregations")
    st.dataframe(df)
