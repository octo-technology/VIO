import streamlit as st


from gcp_binary_storage import GCPBinaryStorage
from models.edge_data import EdgeData
from streamlit_component.edge_section import EdgeSection

EDGES= ["edge1", "edge2"]  


def main():
    # Page configuration
    st.set_page_config(page_title="VIO Hub Viewer", layout="wide")

    # Init variables
    if not st.session_state.get("gcp_client"):
        st.session_state.gcp_client = GCPBinaryStorage()

    for edge_name in EDGES:
        edge_data = EdgeData(name=edge_name)
        edge_data.get_ip(gcp_client=st.session_state.gcp_client)
        edge_data.extract(gcp_client=st.session_state.gcp_client)
        edge_section = EdgeSection(edge_name, edge_data)
        if st.button(key=f"update-{edge_name}", label="Update"):
            edge_section.refresh(st.session_state.gcp_client)
        edge_section.show()
        st.divider()

if __name__ == "__main__":
    main()
