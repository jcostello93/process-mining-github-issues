import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pm4py.statistics.traces.generic.log import case_statistics


def show(filtered_log):
    st.title("Case Durations Over Time")

    filtered_log = filtered_log.copy()

    filtered_log = filtered_log[
        ~filtered_log["concept:name"].str.contains("commented", na=False)
    ]

    properties = {"business_hours": False}

    cases_description = case_statistics.get_cases_description(
        filtered_log, parameters=properties
    )

    start_times = []
    durations = []

    for case_id, desc in cases_description.items():
        if "startTime" in desc and "caseDuration" in desc:
            start_times.append(pd.to_datetime(desc["startTime"], unit="s"))
            durations.append(desc["caseDuration"] // 60 // 60 // 24)

    df = pd.DataFrame({"start_time": start_times, "duration_days": durations})

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["start_time"], df["duration_days"], alpha=0.6)

    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())

    ax.set_xlabel("Year")
    ax.set_ylabel("Case Duration (days)")
    ax.set_title("Case Durations Over Time")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
