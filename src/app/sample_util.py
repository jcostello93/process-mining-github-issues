import streamlit as st
import math
import pm4py


def get(full_log):
    full_log = full_log.copy()
    sample_pct = st.number_input(
        "% of full log to sample during token replay",
        min_value=1,
        max_value=100,
        value=50,
        step=1,
    )

    num_cases = math.floor(full_log["case:concept:name"].nunique() * (sample_pct / 100))

    return pm4py.sample_cases(full_log, num_cases=num_cases)
