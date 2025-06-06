import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show(filtered_log):
    filtered_log = filtered_log.copy()
    filtered_log["date"] = filtered_log["time:timestamp"].dt.date
    event_counts = (
        filtered_log.groupby(["date", "concept:name"])
        .size()
        .reset_index(name="event_count")
    )
    event_counts["date"] = pd.to_datetime(event_counts["date"])

    fig, ax = plt.subplots(figsize=(10, 5))
    for event_type, data in event_counts.groupby("concept:name"):
        ax.plot(
            data["date"],
            data["event_count"],
            marker="o",
            linestyle="-",
            label=event_type,
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Number of Events")
    ax.set_title("Events Over Time")
    ax.legend(
        title="Event Type",
        bbox_to_anchor=(0.5, -0.15),
        loc="upper center",
        ncol=3,
        frameon=False,
    )
    ax.grid()

    st.pyplot(fig)
