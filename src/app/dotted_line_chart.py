import pm4py
import streamlit as st


def show(filtered_log):
    show_legend = st.toggle("Show legend")
    dotted_line_file_name = "dotted_line_chart.png"
    pm4py.save_vis_dotted_chart(
        filtered_log, show_legend=show_legend, file_path=dotted_line_file_name
    )
    st.image(dotted_line_file_name, use_container_width=True)
