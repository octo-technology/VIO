import streamlit as st


from gcp_binary_storage import GCPBinaryStorage
from models.edge_data_manager import EdgeDataManager
from streamlit_component.edge_section import EdgeSection

EDGES= ["edge1", "edge2"]  


def main():
    # Page configuration
    st.set_page_config(page_title="VIO Hub Viewer", layout="wide")

    # Init variables
    if not st.session_state.get("active_edges"):
        st.session_state.gcp_client = GCPBinaryStorage()
        st.session_state.edge_data = EdgeDataManager(edge_names=EDGES)
        st.session_state.edge_data.refresh(st.session_state.gcp_client)
    sidebar(st.session_state.edge_data)


def sidebar(edge_data: EdgeDataManager):
    st.sidebar.markdown(
        "<h1 style='font-size: 2em; text-align: left;'><b>VIO Hub</b></h1>",
        unsafe_allow_html=True,
    )
    st.sidebar.title("Configuration")

    # Refresh data
    if st.sidebar.button("↻"):
        st.session_state.edge_data.refresh(st.session_state.gcp_client)

    for edge_name in EDGES:
        edge_section = EdgeSection(edge_name, edge_data.get_edge_data(edge_name))
        edge_section.show()
        st.divider()


if __name__ == "__main__":
    main()
