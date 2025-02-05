import streamlit as st
import pm4py
from src.app import (
    num_active_cases_over_time,
    num_issues_created_over_time,
    num_events_over_time,
    num_open_issues_over_time,
    pct_closed_over_time,
)


def third_grid(filtered_log):
    # Define file paths for images
    file_paths = {
        "Events Over Days of the Week": "events_over_days_of_week.png",
        "Events Over Hour of the Day": "events_over_hour_of_day.png",
        "Events Over Time": "events_over_time.png",
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
    pm4py.save_vis_events_per_time_graph(
        filtered_log, file_path=file_paths["Events Over Time"]
    )
    pm4py.save_vis_case_duration_graph(
        filtered_log, file_path=file_paths["Case Duration Distribution"]
    )

    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Display images in the grid
    with col1:
        st.image(
            file_paths["Events Over Days of the Week"],
            caption="Events Over Days of the Week",
            use_container_width=True,
        )
    with col2:
        st.image(
            file_paths["Events Over Hour of the Day"],
            caption="Events Over Hour of the Day",
            use_container_width=True,
        )
    with col3:
        st.image(
            file_paths["Events Over Time"],
            caption="Events Over Time",
            use_container_width=True,
        )
    with col4:
        st.image(
            file_paths["Case Duration Distribution"],
            caption="Case Duration Distribution",
            use_container_width=True,
        )


def second_grid(filtered_log):
    filtered_log = filtered_log.copy()

    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # First Chart: Issues Created Over Time
    with col1:
        num_issues_created_over_time.show(filtered_log)

    # Placeholder for additional charts
    with col2:
        num_open_issues_over_time.show(filtered_log)

    with col3:
        num_active_cases_over_time.show(filtered_log)

    with col4:
        num_events_over_time.show(filtered_log)


def first_grid(filtered_log):
    filtered_log = filtered_log.copy()

    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # First Chart: Issues Created Over Time
    with col1:
        pct_closed_over_time.show(filtered_log)

    # Placeholder for additional charts
    with col2:
        dotted_line_file_name = "dotted_line_chart.png"
        pm4py.save_vis_dotted_chart(
            filtered_log, show_legend=False, file_path=dotted_line_file_name
        )
        st.image(dotted_line_file_name, use_container_width=True)

    # with col3:
    #     # num_active_cases_over_time.show(filtered_log)

    # with col4:
    #     # num_events_over_time.show(filtered_log)


def show(filtered_log):
    first_grid(filtered_log)
    second_grid(filtered_log)
    third_grid(filtered_log)
