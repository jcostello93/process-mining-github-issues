import streamlit as st


def show(filtered_log):
    filtered_log = filtered_log.copy()
    st.title("Filtered Event Log")

    st.write(f"📊 **Total Events:** {len(filtered_log)}")
    st.write(f"📂 **Total Cases:** {filtered_log['case:concept:name'].nunique()}")

    search_query = st.text_input("🔍 Search Case Name:", "")

    if search_query:
        filtered_log = filtered_log[
            filtered_log["case:concept:name"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        ]

    st.write("🔍 **Filtered Data:**")
    st.dataframe(filtered_log)
