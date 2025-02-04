import streamlit as st

from gcp_binary_storage import GCPBinaryStorage
from models.edge_data import EdgeData
from models.edge_data_manager import EdgeDataManager
from streamlit_component.edge_section import EdgeSection


def main():
    # Page configuration
    st.set_page_config(page_title="VIO Hub Viewer", layout="wide")

    # Init variables
    if not st.session_state.get("gcp_client"):
        st.session_state.gcp_client = GCPBinaryStorage()

    if not st.session_state.get("edge_data_manager"):
        st.session_state.edge_data_manager = EdgeDataManager()

    if not st.session_state.get("edge_names"):
        st.session_state.edge_names = st.session_state.gcp_client.get_edges_names()

    for edge_name in st.session_state.edge_names:
        if edge_name not in st.session_state.edge_data_manager.get_edges_data_names():
            edge_data = EdgeData(name=edge_name)
            edge_data.get_ip(gcp_client=st.session_state.gcp_client)
            edge_data.extract(gcp_client=st.session_state.gcp_client)
            st.session_state.edge_data_manager.add_edge_data(edge_data)

        edge_data = st.session_state.edge_data_manager.get_edge_data(edge_name)
        edge_section = EdgeSection(edge_name, edge_data)

        if len(edge_section.use_cases_names) > 0:
            edge_section.show()
            st.divider()


if __name__ == "__main__":
    main()
