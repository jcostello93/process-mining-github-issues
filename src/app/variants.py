import streamlit as st
import pm4py
import matplotlib.pyplot as plt
import pandas as pd
import statistics


def show(filtered_log):
    filtered_log = filtered_log.copy()
    st.title("Case Duration & Variants Analysis")

    # Process Variants
    variants = pm4py.statistics.variants.pandas.get.get_variants_count(filtered_log)
    full_variants, variants_times = (
        pm4py.statistics.variants.log.get.get_variants_along_with_case_durations(
            pm4py.convert_to_event_log(filtered_log)
        )
    )

    num_cases = filtered_log["case:concept:name"].nunique()
    sorted_variants = sorted(variants.items(), key=lambda item: item[1], reverse=True)

    # Allow user to select number of top variants to display
    num_variants = st.slider(
        "Number of Top Variants to Show", min_value=1, max_value=len(variants), value=10
    )

    # Extract top variants
    top_variants = sorted_variants[:num_variants]

    # Assign variant indices for the chart (1, 2, 3... instead of long names)
    variant_indices = [f"Variant {i + 1}" for i in range(num_variants)]
    counts = [v for k, v in top_variants]

    # Display Process Variants as Bar Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(variant_indices, counts)  # X-axis: Variants, Y-axis: Counts

    # Remove x-axis label since variant names are too long
    ax.set_xticks([])
    ax.set_xlabel("Variant index")
    ax.set_ylabel("Count")
    ax.set_title(f"Top {num_variants} Process Variants")

    st.pyplot(fig)

    # Display Variant Data in Table Below
    variant_data = {
        "Variant Index": variant_indices,
        "Full Variant Path": [" → ".join(k) for k, v in top_variants],
        "Count": counts,
        "Median duration (hours)": [
            statistics.median(variants_times[k]) // 60 // 60 for k, v in top_variants
        ],
        "% of log": [round((v / num_cases) * 100, 2) for k, v in top_variants],
    }
    df_variants = pd.DataFrame(variant_data)
    st.write("### Variant Details")
    st.dataframe(df_variants)
