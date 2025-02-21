import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show(filtered_log):
    filtered_log = filtered_log.copy()

    case_durations = filtered_log.groupby("case:concept:name")["time:timestamp"].agg(
        ["min", "max"]
    )
    case_durations.columns = ["start_time", "end_time"]
    case_durations = case_durations.sort_values(by="start_time")

    # Calculate the number of active cases over time by tracking start and end events with a daily resolution
    event_points = pd.DataFrame(
        {
            "timestamp": pd.concat(
                [case_durations["start_time"], case_durations["end_time"]]
            ),
            "change": [1] * len(case_durations) + [-1] * len(case_durations),
        }
    )
    event_points = event_points.sort_values(by="timestamp")
    event_points["active_cases"] = event_points["change"].cumsum()
    event_points = (
        event_points.set_index("timestamp").resample("D").mean().reset_index()
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(
        event_points["timestamp"],
        event_points["active_cases"],
        marker="o",
        linestyle="-",
        color="blue",
    )
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Active Cases")
    ax1.set_title("Active Cases Over Time")
    ax1.grid()
    st.pyplot(fig1)
