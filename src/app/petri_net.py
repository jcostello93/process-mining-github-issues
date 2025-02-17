import streamlit as st
import pm4py
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
    pm4py.save_vis_petri_net(net, im, fm, file_path=petri_filename, format="svg")
    st.image(petri_filename, use_container_width=True)

    sample_log = sample_util.get(full_log)
    if st.button("🐢 Evaluate model"):
        evaluate.show(sample_log, net, im, fm)
