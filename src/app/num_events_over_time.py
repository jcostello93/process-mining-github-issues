import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show(filtered_log):
    filtered_log = filtered_log.copy()
    # Convert timestamps to daily event counts
    filtered_log["date"] = filtered_log["time:timestamp"].dt.date  # Extract date
    event_counts = filtered_log.groupby("date").size().reset_index(name="event_count")

    # Convert back to datetime for plotting
    event_counts["date"] = pd.to_datetime(event_counts["date"])

    # Line Chart: Events Over Time
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        event_counts["date"],
        event_counts["event_count"],
        marker="o",
        linestyle="-",
        color="green",
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Number of Events")
    ax.set_title("Events Over Time")
    ax.grid()
    st.pyplot(fig)
