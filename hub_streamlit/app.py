import streamlit as st
from src.infrastructure.cloud_connectors.gcp_connector import get_gcp_client, extract_items
from src.infrastructure.display_items.edge_section import EdgeSection


def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Page configuration
    st.set_page_config(
        page_title="VIO Hub Viewer",
        layout="wide"
    )

    # Init variables
    if "active_edges" not in st.session_state:
        st.session_state.active_edges = []
        st.session_state.active_edges_displays = []
        st.session_state.gcp_client = get_gcp_client()

    full_data = extract_items(st.session_state.gcp_client)
    sidebar(full_data)


def sidebar(full_data):
    st.sidebar.title("# VIO Hub")
    st.sidebar.title("Configuration")

    # Select edge and use case
    activating_edges = st.sidebar.multiselect("Available edges", full_data["edge_list"])

    # Refresh data
    if st.sidebar.button("↻"):
        full_data = extract_items(st.session_state.gcp_client)

    # Computes the page display
    removing_edges = [edge for edge in st.session_state.active_edges if edge not in activating_edges]
    adding_edges = [edge for edge in activating_edges if edge not in st.session_state.active_edges]
    for edge in activating_edges:
        edge_section = EdgeSection(edge, full_data[edge])
        edge_section.show()
        st.session_state.active_edges.append(edge)
        st.session_state.active_edges_displays.append(edge_section)

    for edge in removing_edges:
        index_edge = st.session_state.active_edges.index(edge)
        st.session_state.active_edges.pop(index_edge)
        # st.session_state.active_edges_displays[index_edge].empty()
        st.session_state.active_edges_displays.pop(index_edge)


def select_active_data_sources(folders, edges, use_cases):
    active_data_sources = {"edge_list": edges}
    for edge in edges:
        active_data_sources[edge] = {}
        active_data_sources[edge]["use_case_list"] = use_cases[edge]
        active_data_sources[edge]["edge_ip"] = folders[edge]["edge_ip"]
        for use_case in use_cases[edge]:
            active_data_sources[edge][use_case] = folders[edge][use_case]

    return active_data_sources


# Exécution du script principal
if __name__ == "__main__":
    main()
