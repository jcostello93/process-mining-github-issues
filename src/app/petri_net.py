import streamlit as st
import pm4py
from pm4py.visualization.petri_net import visualizer as petri_net_visualizer


def show(filtered_log):
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

    if st.button("🔍 Open Petri Net with Frequencies in New Window"):
        gviz_frequency = petri_net_visualizer.apply(
            net,
            im,
            fm,
            variant=petri_net_visualizer.Variants.FREQUENCY,
            log=filtered_log,
        )

        petri_net_visualizer.view(gviz_frequency)
