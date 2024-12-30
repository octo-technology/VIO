import streamlit as st
from src.edge_services import get_active_config
from src.infrastructure.display_items.use_case_section import UseCaseSection


class EdgeSection:
    def __init__(self, edge: str, data: dict):
        self.edge = edge
        self.edge_ip = data["edge_ip"]
        self.use_cases = data["use_case_list"]
        self.data = data

        self.edge_title_placeholder = st.columns(3)
        self.title_placeholder = self.edge_title_placeholder[0].empty()
        self.button_placeholder = self.edge_title_placeholder[1].empty()
        self.active_config_placeholder = self.edge_title_placeholder[2].empty()

        self.use_case_sections = None
        self.selected_use_case = self.use_cases[0]

    def show(self):
        self.selected_use_case = self.button_placeholder.selectbox("Displayed use case", self.use_cases)
        self.title_placeholder.markdown(f"### ⏳: {self.edge.replace('_', ' ')}")

        active_config = get_active_config(self.edge_ip)
        if active_config is not False:
                self.active_config_placeholder.write(f"Active configuration: {active_config['name']}")
                self.title_placeholder.markdown(f"### 🟢 {self.edge.replace('_', ' ')}")
        else:
                self.active_config_placeholder.write("")
                self.title_placeholder.markdown(f"### 🔴 {self.edge.replace('_', ' ')}")

        self.show_use_case(self.selected_use_case)

    def show_use_case(self, use_case):
        if self.use_case_sections is not None:
            self.use_case_sections.empty()

        self.use_case_sections = UseCaseSection(use_case, self.data[use_case])
        self.use_case_sections.show()
