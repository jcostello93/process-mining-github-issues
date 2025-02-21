import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd


def show(filtered_log):
    filtered_log["case:created_at"] = pd.to_datetime(
        filtered_log["case:created_at"], utc=True
    )

    # Aggregate number of issues created in 4 month periods
    cases = filtered_log[["case:concept:name", "case:created_at"]].drop_duplicates()
    issues_created = cases.groupby(cases["case:created_at"].dt.date).size()
    issues_created.index = pd.to_datetime(issues_created.index)
    aggregation_frequency = "4M"
    issues_created = issues_created.resample(aggregation_frequency).sum()

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(issues_created.index, issues_created.values, marker="o", linestyle="-")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Number of Issues Created")
    ax1.set_title("Number of Issues Created Over Time")
    ax1.grid()
    plt.xticks(rotation=45)
    st.pyplot(fig1)
