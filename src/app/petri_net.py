import streamlit as st
import pm4py
from collections import Counter
import pandas as pd
from src.app import evaluate, sample_util


def show(full_log, filtered_log):
    full_log = full_log.copy()
    st.title("Petri net")

    # Generate a Petri Net
    noise_threshold_petri = st.slider(
        "Noise Threshold Petri", min_value=0.0, max_value=1.0, value=0.0, step=0.05
    )
    net, im, fm = pm4py.discover_petri_net_inductive(
        filtered_log, noise_threshold=noise_threshold_petri
    )

    petri_filename = "petri_net.svg"
    rankdir = st.selectbox("Select Petri net layout direction:", ["LR", "TB"])
    pm4py.save_vis_petri_net(
        net, im, fm, file_path=petri_filename, rankdir=rankdir, format="svg"
    )
    st.image(petri_filename, use_container_width=True)

    st.title("Play out log simulation")
    num_traces = st.number_input(
        "Number of traces to simulate",
        min_value=1,
        max_value=1000,
        value=100,
        step=1,
    )
    max_trace_length = st.number_input(
        "Max simulated trace length",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
    )
    simulated_log = pm4py.play_out(
        net,
        im,
        fm,
        parameters={
            "add_only_if_fm_is_reached": True,
            "noTraces": num_traces,
            "maxTraceLength": max_trace_length,
        },
    )

    path_strings = []
    for trace in simulated_log:
        activity_names = [event["concept:name"] for event in trace]
        path_string = " -> ".join(activity_names)
        path_strings.append(path_string)

    path_counts = Counter(path_strings)

    df = pd.DataFrame(path_counts.items(), columns=["Path", "Count"])
    df = df.sort_values(by="Count", ascending=False)
    st.dataframe(df, use_container_width=True)

    st.title("Token-based replay")
    sample_log = sample_util.get(full_log)
    if st.button("🐢 Evaluate model"):
        evaluate.show(sample_log, net, im, fm)
