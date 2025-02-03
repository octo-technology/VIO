import streamlit as st

from gcp_binary_storage import GCPBinaryStorage
from models.edge_data import EdgeData
from streamlit_component.edge_section import EdgeSection

EDGES = ["edge2", "localhost"]


def main():
    # Page configuration
    st.set_page_config(page_title="VIO Hub Viewer", layout="wide")

    # Init variables
    if not st.session_state.get("gcp_client"):
        st.session_state.gcp_client = GCPBinaryStorage()

    if not st.session_state.get("edge_data_dict"):
        st.session_state.edge_data_dict = {}

    for edge_name in EDGES:
        if edge_name not in st.session_state.edge_data_dict.keys():
            edge_data = EdgeData(name=edge_name)
            edge_data.get_ip(gcp_client=st.session_state.gcp_client)
            edge_data.extract(gcp_client=st.session_state.gcp_client)
            st.session_state.edge_data_dict[edge_name] = edge_data

        edge_data = st.session_state.edge_data_dict[edge_name]
        edge_section = EdgeSection(edge_name, edge_data)

        if len(edge_section.use_cases_names) > 0:
            edge_section.show()
            st.divider()


if __name__ == "__main__":
    main()
