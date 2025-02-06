import streamlit as st
import pm4py


def show(filtered_log):
    st.title("BPMN")
    noise_threshold_bpmn = st.slider(
        "Noise Threshold BPMN", min_value=0.0, max_value=1.0, value=0.0, step=0.05
    )
    bpmn_diagram = pm4py.discover_bpmn_inductive(
        filtered_log, noise_threshold=noise_threshold_bpmn
    )
    bpmn_filename = "bpmn_net.svg"
    pm4py.save_vis_bpmn(bpmn_diagram, file_path=bpmn_filename, format="svg")
    st.image(bpmn_filename, use_container_width=True)
