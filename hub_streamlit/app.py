import streamlit as st
from src.infrastructure.gcp_connector import get_gcp_client, extract_items
from src.edge_services import get_active_config


def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Init variables
    if "edges" not in st.session_state:
        active_data_sources = None
        st.session_state.edges = []
        st.session_state.usecase = {}
    folders = extract_items(get_gcp_client())

    # Page configuration
    st.set_page_config(
        page_title="Mon Application Streamlit",
        page_icon="🔦",
        layout="wide"
    )

    # Sidebar parameters
    st.sidebar.title("Configuration")
    active_data_sources = sidebar(folders)

    # Page content
    st.title("VIO Hub")
    st.write("""
    This application is designed to monitor edge fleet and analyze the data in real-time.
    """)

    if active_data_sources:
        display_pictures(active_data_sources, 4)

### Faire a l'horizontal
### Séparer les caméras


def sidebar(folders):
    # Select edge and use case
    active_edges = st.sidebar.multiselect("Available edges", st.session_state.edges)
    all_active_use_cases = {}
    for edge in active_edges:
        list_use_cases = st.session_state.usecase[edge]
        all_active_use_cases[edge] = []
        all_active_use_cases[edge] = st.sidebar.multiselect(f"Select use cases for {edge.replace('-', ' ')}", list_use_cases)
    active_data_sources = select_active_data_sources(folders, active_edges, all_active_use_cases)

    # Refresh data
    if st.sidebar.button("↻"):
        folders = extract_items(get_gcp_client())
        refresh_sidebar_parameters(folders)

    return active_data_sources


def refresh_sidebar_parameters(folders):
    list_edges = folders["edge_list"]
    st.session_state.edges = list_edges
    for edge in list_edges:
        list_use_cases = folders[edge]["use_case_list"]
        st.session_state.usecase[edge] = list_use_cases


def select_active_data_sources(folders, edges, use_cases):
    active_data_sources = {"edge_list": edges}
    for edge in edges:
        active_data_sources[edge] = {}
        active_data_sources[edge]["use_case_list"] = use_cases[edge]
        active_data_sources[edge]["edge_ip"] = folders[edge]["edge_ip"]
        for use_case in use_cases[edge]:
            active_data_sources[edge][use_case] = folders[edge][use_case]

    return active_data_sources


def display_pictures(active_data_sources, n_cols):
    # Display pictures from gcp bucket
    for edge in active_data_sources["edge_list"]:
        edge_data = active_data_sources[edge]
        display_edge_information(edge, edge_ip=edge_data["edge_ip"])

        for use_case in edge_data["use_case_list"]:
            use_case_data = edge_data[use_case]
            st.markdown(f"##### Use case: {use_case.replace('_', ' ').title()}")
            columns_syst = st.columns(n_cols)
            idx_col = 0
            for item_id in use_case_data["item_list"]:
                item_data = use_case_data[item_id]
                if "pictures" not in item_data or "metadata" not in item_data:
                    continue
                for picture in item_data["pictures"]:
                    columns_syst[idx_col].image(picture, caption=f"Creation date: {item_data['creation_date'].strftime('%Y-%m-%d %H:%M:%S')}",
                                                use_container_width=True)
                    idx_col += 1


def display_edge_information(edge: str, edge_ip: str):
    title_placeholder = st.empty()
    title_placeholder.markdown(f"### Edge: {edge.replace('_', ' ')}")
    text_placeholder = st.empty()
    text_placeholder.write("⏳Thinking...")

    active_config = get_active_config(edge_ip)
    if active_config is not False:
        text_placeholder.write(f"Active configuration: {active_config['name']}")
        title_placeholder.markdown(f"### 🟢 {edge.replace('_', ' ')}")
    else:
        text_placeholder.write("")
        title_placeholder.markdown(f"### 🔴 {edge.replace('_', ' ')}")



# Exécution du script principal
if __name__ == "__main__":
    main()
