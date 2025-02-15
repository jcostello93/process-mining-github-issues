import streamlit as st
import pm4py
from pm4py.algo.filtering.dfg.dfg_filtering import filter_dfg_on_activities_percentage
from pm4py.algo.filtering.dfg.dfg_filtering import filter_dfg_on_paths_percentage
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.algo.discovery.dfg.variants import clean_time as clean_dfg_time
from pm4py.visualization.dfg.variants import timeline as timeline_gviz_generator
from src.app import evaluate, sample_util


def show(full_log, filtered_log):
    full_log = full_log.copy()
    st.title("DFG")

    # Discover the frequency DFG using activites and paths to filter
    activities = pm4py.get_event_attribute_values(filtered_log, "concept:name")
    frequency_dfg, start_activities, end_activities = pm4py.discover_dfg(filtered_log)
    activities_perc = st.slider(
        "Activities Percentage", min_value=0.0, max_value=1.0, value=0.90, step=0.05
    )
    paths_perc = st.slider(
        "Paths Percentage", min_value=0.0, max_value=1.0, value=0.10, step=0.05
    )
    max_num_edges = st.slider(
        "Max Number of Edges", min_value=1, max_value=500, value=100, step=1
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

    # Discover the performance DFG (does not support activites and paths filtering)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(
        filtered_log
    )

    # Use the frequency DFG to filter the performance DFG
    removal_list = []
    for edge in performance_dfg:
        if performance_dfg[edge]["median"] == 0.0:
            removal_list.append(edge)

        if edge not in frequency_dfg:
            removal_list.append(edge)

    for edge in removal_list:
        if edge in performance_dfg:
            del performance_dfg[edge]

    pm4py.save_vis_dfg(
        frequency_dfg,
        start_activities,
        end_activities,
        max_num_edges=max_num_edges,
        rankdir="LR",
        file_path="frequency_dfg.svg",
        format="svg",
    )
    pm4py.save_vis_performance_dfg(
        performance_dfg,
        start_activities,
        end_activities,
        aggregation_measure="sum",
        rankdir="LR",
        file_path="performance_dfg_sum.svg",
        format="svg",
    )
    pm4py.save_vis_performance_dfg(
        performance_dfg,
        start_activities,
        end_activities,
        aggregation_measure="median",
        rankdir="LR",
        file_path="performance_dfg_median.svg",
        format="svg",
    )

    st.image("frequency_dfg.svg", use_container_width=False)

    sample_log = sample_util.get(full_log)
    if st.button("🐢 Evaluate model (via petri net)"):
        pnet, pim, pfm = pm4py.convert_to_petri_net(
            frequency_dfg, start_activities, end_activities
        )
        # petri_filename = "petri_dfg_net.svg"
        # pm4py.save_vis_petri_net(pnet, pim, pfm, file_path=petri_filename, format="svg")
        # st.image(petri_filename, use_container_width=True)
        evaluate.show(sample_log, pnet, pim, pfm)

    st.image("performance_dfg_sum.svg", use_container_width=False)
    st.image("performance_dfg_median.svg", use_container_width=False)

    try:
        dfg_time = clean_dfg_time.apply(filtered_log)
        gviz = timeline_gviz_generator.apply(
            frequency_dfg,
            dfg_time,
            parameters={
                "max_no_of_edges_in_diagram": max_num_edges,
                "start_activities": start_activities,
                "end_activities": end_activities,
            },
        )
        dfg_filename = "dfg_timeline.png"
        dfg_visualizer.save(gviz, dfg_filename)

        st.image(dfg_filename, use_container_width=False)
    except Exception:
        print("Could not load timeline")
