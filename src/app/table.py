import streamlit as st


def show(filtered_log):
    log = filtered_log.copy()
    st.title("Filtered Event Log")

    st.write(f"📊 **Total Events:** {len(log)}")
    st.write(f"📂 **Total Cases:** {log['case:concept:name'].nunique()}")

    search_query = st.text_input("🔍 Search Case Name:", "")

    if search_query:
        log = log[
            log["case:concept:name"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        ]

    st.write("🔍 **Filtered Data:**")
    st.dataframe(log)
