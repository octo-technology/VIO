import streamlit as st

from src.edge_services import get_active_config
from src.infrastructure.cloud_connectors.edge_data import Edge
from src.infrastructure.display_items.use_case_section import UseCaseSection


class EdgeSection:
    def __init__(self, edge_name: str, edge_data: Edge):
        self.edge_name = edge_name
        self.edge_name_with_whitespaces = self.edge_name.replace("_", " ")
        self.edge_ip = edge_data.edge_ip
        self.use_cases = edge_data.use_case_names
        self.data = edge_data

        self.edge_title_placeholder = st.columns(3)
        self.title_placeholder = self.edge_title_placeholder[0].empty()
        self.button_placeholder = self.edge_title_placeholder[2].empty()
        self.active_config_placeholder = self.edge_title_placeholder[1].empty()

        self.use_case_sections = None
        self.selected_use_case = self.use_cases[0]

    def show(self):
        self.selected_use_case = self.button_placeholder.selectbox(
            "Select a use case", options=self.use_cases, label_visibility="collapsed"
        )  # TODO: fix if two edge has the same use_case it won't work because of duplicate keys on two different selectbox objects
        self.title_placeholder.markdown(f"### ⏳ {self.edge_name_with_whitespaces}")

        active_config = get_active_config(self.edge_ip)
        if active_config:
            self.active_config_placeholder.write(
                f"Active configuration: {active_config.get('name')}"
            )
            self.title_placeholder.markdown(f"### 🟢 {self.edge_name_with_whitespaces}")
        else:
            self.active_config_placeholder.write("")
            self.title_placeholder.markdown(f"### 🔴 {self.edge_name_with_whitespaces}")

        self.show_use_case(self.selected_use_case)

    def show_use_case(self, use_case: str):
        if self.use_case_sections:
            self.use_case_sections.empty()

        self.use_case_sections = UseCaseSection(use_case, self.data.use_cases[use_case])
        self.use_case_sections.show()
