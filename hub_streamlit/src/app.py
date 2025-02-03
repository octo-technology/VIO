import streamlit as st
from google.cloud.storage import Client

from data_extraction import extract_items
from models.edge_data_manager import EdgeDataManager
from streamlit_component.edge_section import EdgeSection


def main():
    # Page configuration
    st.set_page_config(page_title="VIO Hub Viewer", layout="wide")

    # Init variables
    if not st.session_state.get("active_edges"):
        st.session_state.active_edges = []
        st.session_state.gcp_client = Client()

        st.session_state.edge_data = extract_items(st.session_state.gcp_client)

    sidebar(st.session_state.edge_data)


def sidebar(edge_data: EdgeDataManager):
    st.sidebar.markdown(
        "<h1 style='font-size: 2em; text-align: left;'><b>VIO Hub</b></h1>",
        unsafe_allow_html=True,
    )
    st.sidebar.title("Configuration")

    # Select edge and use case
    selected_edges = st.sidebar.multiselect(
        "Available edges", edge_data.get_edge_names()
    )
    st.session_state.active_edges = selected_edges

    # Refresh data
    if st.sidebar.button("↻"):
        st.session_state.edge_data = extract_items(st.session_state.gcp_client)

    # Computes the page display
    removing_edges = [
        edge for edge in st.session_state.active_edges if edge not in selected_edges
    ]

    for edge_name in selected_edges:
        edge_section = EdgeSection(edge_name, edge_data.get_edge(edge_name))
        edge_section.show()
        st.divider()

    for edge_name in removing_edges:
        edge_index = st.session_state.active_edges.index(edge_name)
        st.session_state.active_edges.pop(edge_index)


if __name__ == "__main__":
    main()
