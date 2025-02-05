import streamlit as st
import pm4py
from src.app import bpmn, dfg, petri_net


def show(filtered_log):
    petri_net.show(filtered_log)
    bpmn.show(filtered_log)
    dfg.show(filtered_log)
    performance_spectrum_file_path = "performance_spectrum.png"
    pm4py.save_vis_performance_spectrum(
        filtered_log,
        ["created", "not_planned"],
        file_path=performance_spectrum_file_path,
    )
    st.image(performance_spectrum_file_path, use_container_width=False)
