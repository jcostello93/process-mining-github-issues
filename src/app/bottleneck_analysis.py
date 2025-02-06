import streamlit as st
import pm4py
from src.app import case_duration_over_time, dotted_line_chart, dfg


def show(filtered_log):
    performance_spectrum_file_path = "performance_spectrum.png"

    # Event options
    st.write("🔹 Enter Events (Comma-Separated)")
    event_string = st.text_area("Event Sequence", "created, not_planned")
    ordered_events = [e.strip() for e in event_string.split(",") if e.strip()]

    if len(ordered_events) < 2:
        st.error("Please enter at least two events.")

    pm4py.save_vis_performance_spectrum(
        filtered_log,
        ordered_events,
        file_path=performance_spectrum_file_path,
    )
    st.image(performance_spectrum_file_path, use_container_width=False)
    dotted_line_chart.show(filtered_log)

    case_duration_over_time.show(filtered_log)
    dfg.show(filtered_log)
