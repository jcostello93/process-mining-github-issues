import streamlit as st
import pm4py
from pm4py.statistics.traces.generic.log.case_statistics import get_median_case_duration
from pm4py.statistics.traces.generic.log.case_arrival import get_case_dispersion_avg
from src.app import (
    case_duration_distribution,
    dotted_line_chart,
    num_active_cases_over_time,
    num_issues_created_over_time,
    num_events_over_time,
    num_open_issues_over_time,
)


def second_grid(filtered_log):
    # Define file paths for images
    file_paths = {
        "Events Over Days of the Week": "events_over_days_of_week.png",
        "Events Over Hour of the Day": "events_over_hour_of_day.png",
        "Case Duration Distribution": "case_duration.png",
    }

    # Generate PM4Py visualizations
    pm4py.save_vis_events_distribution_graph(
        filtered_log,
        distr_type="days_week",
        file_path=file_paths["Events Over Days of the Week"],
    )
    pm4py.save_vis_events_distribution_graph(
        filtered_log,
        distr_type="hours",
        file_path=file_paths["Events Over Hour of the Day"],
    )
    pm4py.save_vis_case_duration_graph(
        filtered_log, file_path=file_paths["Case Duration Distribution"]
    )

    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Display images in the grid
    with col1:
        num_events_over_time.show(filtered_log)
    with col2:
        num_issues_created_over_time.show(filtered_log)
    with col3:
        st.image(
            file_paths["Events Over Days of the Week"],
            caption="Events Over Days of the Week",
            use_container_width=True,
        )
    with col4:
        st.image(
            file_paths["Events Over Hour of the Day"],
            caption="Events Over Hour of the Day",
            use_container_width=True,
        )


def first_grid(filtered_log):
    filtered_log = filtered_log.copy()

    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # First Chart: Issues Created Over Time
    with col1:
        dotted_line_chart.show(filtered_log)

    # Placeholder for additional charts
    with col2:
        case_duration_distribution.show(filtered_log)

    with col3:
        num_active_cases_over_time.show(filtered_log)

    with col4:
        num_open_issues_over_time.show(filtered_log)


def show(filtered_log):
    # Copy log to avoid modifying original
    cell_log = filtered_log.copy()

    # Compute Metrics
    median_case_duration = get_median_case_duration(cell_log)
    case_arrival_average = pm4py.get_case_arrival_average(cell_log)
    case_dispersion_ratio = get_case_dispersion_avg(cell_log)

    # Display Metrics
    st.write(f"📏 **Median Case Duration:** {median_case_duration // 60 // 60} hours")
    st.write(
        f"⏳ **Avg. Time Between Case Arrivals:** {case_arrival_average // 60 // 60} hours"
    )
    st.write(
        f"📉 **Avg. Time Between Case Finishing:** {case_dispersion_ratio // 60 // 60} hours"
    )

    first_grid(filtered_log)
    second_grid(filtered_log)
