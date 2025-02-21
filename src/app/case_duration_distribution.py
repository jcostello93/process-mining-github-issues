import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pm4py.statistics.traces.generic.log import case_statistics


def show(filtered_log):
    filtered_log = filtered_log.copy()

    cases_description = case_statistics.get_cases_description(filtered_log)
    durations = []
    for case_id, desc in cases_description.items():
        if "caseDuration" in desc:
            durations.append(desc["caseDuration"] // 60 // 60 // 24)

    df = pd.DataFrame({"durations": durations})

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(
        df["durations"],
        bins=[i * 30 for i in range(13)],
        edgecolor="black",
        alpha=0.7,
    )
    ax.set_xlim(0, 365)

    ax.set_xlabel("Case Duration (Days)")
    ax.set_ylabel("Number of Cases")
    ax.set_title("Distribution of Case Durations")

    plt.tight_layout()

    # Display the plot
    st.pyplot(fig)
