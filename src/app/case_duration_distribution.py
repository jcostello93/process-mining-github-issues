import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pm4py.statistics.traces.generic.log import case_statistics


def show(filtered_log):
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

    durations = []

    # Extract case durations
    for case_id, desc in cases_description.items():
        if "caseDuration" in desc:
            durations.append(
                desc["caseDuration"] // 60 // 60 // 24
            )  # Convert seconds to days

    # Create DataFrame
    df = pd.DataFrame({"duration_days": durations})

    # Create histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df["duration_days"], bins=30, edgecolor="black", alpha=0.7)

    ax.set_xlabel("Case Duration (Days)")
    ax.set_ylabel("Number of Cases")
    ax.set_title("Distribution of Case Durations")

    plt.tight_layout()

    # Display the plot
    st.pyplot(fig)
