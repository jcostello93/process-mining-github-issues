import streamlit as st
import matplotlib.pyplot as plt
from pm4py.statistics.traces.generic.log import case_statistics


def show(filtered_log):
    """Displays a scatter plot of case durations over time."""
    st.title("Case Durations Over Time")

    # Copy log to avoid modifying original
    filtered_log = filtered_log.copy()

    # Filter out "commented" events
    filtered_log = filtered_log[
        ~filtered_log["concept:name"].str.contains("commented", na=False)
    ]

    # Define properties for case statistics
    properties = {"business_hours": False}

    # Get case descriptions
    cases_description = case_statistics.get_cases_description(
        filtered_log, parameters=properties
    )

    start_times = []
    durations = []

    # Extract start times and case durations
    for case_id, desc in cases_description.items():
        if "startTime" in desc and "caseDuration" in desc:
            start_times.append(desc["startTime"])
            durations.append(desc["caseDuration"] // 60 // 60 // 24)  # Convert to days

    # Create and display scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(start_times, durations, alpha=0.6)
    ax.set_xlabel("Case Start Time")
    ax.set_ylabel("Case Duration (days)")
    ax.set_title("Case Durations Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
