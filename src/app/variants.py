import streamlit as st
import pm4py
import matplotlib.pyplot as plt
from pm4py.statistics.traces.generic.log.case_statistics import get_median_case_duration
from pm4py.statistics.traces.generic.log.case_arrival import get_case_dispersion_avg


def show(filtered_log):
    st.title("Case Duration & Variants Analysis")

    # Copy log to avoid modifying original
    cell_log = filtered_log.copy()

    # Compute Metrics
    median_case_duration = get_median_case_duration(cell_log)
    case_arrival_average = pm4py.get_case_arrival_average(cell_log)
    case_dispersion_ratio = get_case_dispersion_avg(cell_log)

    # Display Metrics
    st.write(
        f"📏 **Median Case Duration:** {median_case_duration // 60 // 60 // 24} days"
    )
    st.write(
        f"⏳ **Avg. Time Between Case Arrivals:** {case_arrival_average // 60 // 60} hours"
    )
    st.write(
        f"📉 **Avg. Time Between Case Finishing:** {case_dispersion_ratio // 60 // 60} hours"
    )

    # Process Variants
    variants = pm4py.statistics.variants.pandas.get.get_variants_count(filtered_log)
    sorted_variants = sorted(variants.items(), key=lambda item: item[1], reverse=True)

    # Allow user to select number of top variants to display
    num_variants = st.slider(
        "Number of Top Variants to Show", min_value=1, max_value=20, value=10
    )

    # Extract top variants
    top_variants = sorted_variants[:num_variants]
    labels = [" → ".join(k) for k, v in top_variants]
    counts = [v for k, v in top_variants]

    # Display Process Variants as Bar Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(labels[::-1], counts[::-1])  # Reverse for better visualization
    ax.set_xlabel("Count")
    ax.set_ylabel("Variant")
    ax.set_title(f"Top {num_variants} Process Variants")

    st.pyplot(fig)
