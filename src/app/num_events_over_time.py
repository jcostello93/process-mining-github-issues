import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show(filtered_log):
    filtered_log = filtered_log.copy()

    # Extract date from timestamp
    filtered_log["date"] = filtered_log["time:timestamp"].dt.date

    # Group by date & concept:name (event type)
    event_counts = (
        filtered_log.groupby(["date", "concept:name"])
        .size()
        .reset_index(name="event_count")
    )

    # Convert date back to datetime for plotting
    event_counts["date"] = pd.to_datetime(event_counts["date"])

    # Plot Events Over Time (One Line Per Event Type)
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
    ax.set_title("Events Over Time (Grouped by Event Type)")
    ax.legend(title="Event Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid()

    st.pyplot(fig)
