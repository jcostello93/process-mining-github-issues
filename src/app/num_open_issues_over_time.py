import streamlit as st
import matplotlib.pyplot as plt


def show(filtered_log):
    filtered_log = filtered_log.copy()

    cases = filtered_log[
        ["case:concept:name", "case:created_at", "case:closed_at"]
    ].drop_duplicates()

    timestamps = sorted(
        set(cases["case:created_at"]).union(set(cases["case:closed_at"].dropna()))
    )
    open_tickets = []
    current_open = 0
    for timestamp in timestamps:
        opened = (cases["case:created_at"] == timestamp).sum()
        closed = (cases["case:closed_at"] == timestamp).sum()
        current_open += opened - closed
        open_tickets.append(current_open)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(timestamps, open_tickets, marker="o", linestyle="-")
    ax.set_xlabel("Time")
    ax.set_ylabel("Number of Open Issues")
    ax.set_title("Number of Open Issues Over Time")
    ax.grid()
    plt.xticks(rotation=45)

    st.pyplot(fig)
