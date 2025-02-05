import streamlit as st
import matplotlib.pyplot as plt


def show(filtered_log):
    st.title("Issue Distribution")

    if len(filtered_log) == 0:
        st.write("The dataframe is empty")
        return

    # Convert log to DataFrame
    df_filtered = filtered_log
    print(df_filtered.head())
    # Plot issue distribution
    fig, ax = plt.subplots()
    df_filtered["concept:name"].value_counts().plot(
        kind="bar", ax=ax, color="royalblue"
    )
    ax.set_xlabel("Event Type")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Events")

    st.pyplot(fig)

    # Download button
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    filename = st.text_input("Enter filename for download:", "filtered_log.csv")
    st.download_button(
        label="Download CSV", data=csv, file_name=filename, mime="text/csv"
    )
