import streamlit as st
import pm4py
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.organizational_mining.sna import algorithm as sna_algorithm
from pm4py.visualization.sna import visualizer as sna_vis


def get_attributes_set(log, field):
    try:
        attributes_set = set(pm4py.get_event_attribute_values(log, field).keys())
    except Exception:
        attributes_set = set()

    return attributes_set


def show(filtered_log):
    handover_factor = st.number_input(
        "Handover factor", min_value=1, max_value=100000000, value=100
    )
    working_together_factor = st.number_input(
        "Working together factor", min_value=1, max_value=100000000, value=10
    )
    subcontracting_factor = st.number_input(
        "Subcontracting factor", min_value=1, max_value=100000000, value=1000
    )

    handover_weight_threshold = 1 / handover_factor
    working_together_weight_threshold = 1 / working_together_factor
    subcontracting_weight_threshold = 1 / subcontracting_factor

    # Load and Filter Log
    st.title("Social Network Analysis")

    if st.button("🐢 Run analysis"):
        # Remove deleted members
        filtered_log = attributes_filter.apply(
            filtered_log,
            values={"Ghost"},
            parameters={
                attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                attributes_filter.Parameters.POSITIVE: False,
            },
        )

        st.success("✅ Log filtered successfully!")

        # Apply SNA Algorithms
        st.write("📊 **Generating Social Network Visualizations**")

        sna_types = {
            "Handover Log": sna_algorithm.Variants.HANDOVER_LOG,
            "Working Together Log": sna_algorithm.Variants.WORKING_TOGETHER_LOG,
            "Subcontracting Log": sna_algorithm.Variants.SUBCONTRACTING_LOG,
        }

        sna_thresholds = {
            "Handover Log": handover_weight_threshold,
            "Working Together Log": working_together_weight_threshold,
            "Subcontracting Log": subcontracting_weight_threshold,
        }

        sna_outputs = {}

        for label, variant in sna_types.items():
            sna_values = sna_algorithm.apply(filtered_log, variant=variant)
            gviz = sna_vis.apply(
                sna_values,
                variant=sna_vis.Variants.PYVIS,
                parameters={
                    sna_vis.Variants.PYVIS.value.Parameters.WEIGHT_THRESHOLD: sna_thresholds[
                        label
                    ]
                },
            )

            # Save and Display Visualization
            filename = f"{label.lower().replace(' ', '_')}.html"
            sna_vis.save(gviz, variant=sna_vis.Variants.PYVIS, dest_file=filename)

            sna_outputs[label] = filename

        # Show Visualizations in Streamlit
        for label, filename in sna_outputs.items():
            st.subheader(f"📌 {label}")
            with open(filename, "r", encoding="utf-8") as f:
                html_code = f.read()
            st.components.v1.html(html_code, height=600, scrolling=True)

            # Download Button
            with open(filename, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download {label} Visualization",
                    data=file,
                    file_name=filename,
                    mime="text/html",
                )
