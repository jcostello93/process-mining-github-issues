import streamlit as st
import pm4py
from pm4py.statistics.traces.generic.log.case_statistics import get_median_case_duration
from pm4py.statistics.traces.generic.log.case_arrival import get_case_dispersion_avg
from src.app import (
    dotted_line_chart,
    num_issues_created_over_time,
    num_events_over_time,
    num_open_issues_over_time,
)


def first_grid(filtered_log):
    filtered_log = filtered_log.copy()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        dotted_line_chart.show(filtered_log)

    with col2:
        num_open_issues_over_time.show(filtered_log)

    with col3:
        num_issues_created_over_time.show(filtered_log)

    with col4:
        num_events_over_time.show(filtered_log)


def show(filtered_log):
    cell_log = filtered_log.copy()

    median_case_duration = get_median_case_duration(cell_log)
    case_arrival_average = pm4py.get_case_arrival_average(cell_log)
    case_dispersion_ratio = get_case_dispersion_avg(cell_log)

    st.write(f"📏 **Median Case Duration:** {median_case_duration // 60 // 60} hours")
    st.write(
        f"⏳ **Avg. Time Between Case Arrivals:** {case_arrival_average // 60 // 60} hours"
    )
    st.write(
        f"📉 **Avg. Time Between Case Finishing:** {case_dispersion_ratio // 60 // 60} hours"
    )

    first_grid(filtered_log)
