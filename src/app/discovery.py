import streamlit as st
import pm4py


def show(filtered_log):
    st.title("Process Model (Petri Net)")

    # Generate a Petri Net
    net, im, fm = pm4py.discover_petri_net_inductive(filtered_log)

    # Visualize Petri Net
    petri_filename = st.text_input("Enter filename for download:", "petri_net.svg")
    pm4py.save_vis_petri_net(net, im, fm, file_path=petri_filename, format="svg")
    st.image(petri_filename, use_container_width=True)

    with open(petri_filename, "rb") as f:
        st.download_button(
            label="Download Petri Net",
            data=f,
            file_name=petri_filename,
            mime="image/svg",
        )
