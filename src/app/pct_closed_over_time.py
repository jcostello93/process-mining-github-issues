import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pm4py


def show(filtered_log):
    filtered_log = filtered_log.copy()

    filtered_log["time:timestamp"] = pd.to_datetime(filtered_log["time:timestamp"])

    # Convert DataFrame to PM4Py event log
    event_log = pm4py.convert_to_event_log(filtered_log)
    case_endings = []
    for trace in event_log:
        last_event = trace[-1]
        case_endings.append(
            {
                "time:timestamp": last_event["time:timestamp"],
                "concept:name": last_event["concept:name"],
            }
        )

    endings_df = pd.DataFrame(case_endings)
    endings_df["time:timestamp"] = pd.to_datetime(endings_df["time:timestamp"])
    endings_df["period"] = endings_df["time:timestamp"].dt.to_period(
        "M"
    )  # Group by month
    summary = (
        endings_df.groupby(["period", "concept:name"]).size().unstack(fill_value=0)
    )
    summary["total"] = summary.sum(axis=1)
    summary["closed_pct"] = (summary.get("closed", 0) / summary["total"]) * 100
    summary["not_planned_pct"] = (
        summary.get("not_planned", 0) / summary["total"]
    ) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        summary.index.astype(str), summary["closed_pct"], marker="o", label="Closed"
    )
    ax.plot(
        summary.index.astype(str),
        summary["not_planned_pct"],
        marker="o",
        label="Not Planned",
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Percentage of Cases")
    ax.set_title('Percentage of Cases Ending in "Closed" vs "Not Planned" Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    ax.grid(True)

    st.pyplot(fig)
