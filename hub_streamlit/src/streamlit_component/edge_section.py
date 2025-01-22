import streamlit as st

from edge_healthcheck import get_supervisor_active_config
from models.edge import Edge
from streamlit_component.use_case_section import UseCaseSection


class EdgeSection:
    def __init__(self, edge_name: str, edge: Edge):
        self.edge_name = edge_name
        self.edge_name_with_whitespaces = self.edge_name.replace("_", " ")
        self.edge_ip = edge.edge_ip
        self.use_cases_names = edge.use_cases_names
        self.use_cases = edge.use_cases

        (
            self.title_placeholder,
            self.active_config_placeholder,
            self.button_placeholder,
        ) = st.columns(3)

        self.use_case_sections = None
        self.selected_use_case = self.use_cases_names[0]

    def show(self):
        self.selected_use_case = self.button_placeholder.selectbox(
            "Select a use case",
            options=self.use_cases_names,
            label_visibility="collapsed",
            key=self.edge_name,
        )

        with st.spinner("Getting active config"):
            active_config = get_supervisor_active_config(self.edge_ip)

        if active_config:
            active_config_placeholder = (
                f"##### Active configuration: {active_config.get('name')}"
            )
            title_placeholder = f"##### 🟢 {self.edge_name_with_whitespaces}"
        else:
            active_config_placeholder = ""
            title_placeholder = f"##### 🔴 {self.edge_name_with_whitespaces}"

        self.active_config_placeholder.markdown(active_config_placeholder)
        self.title_placeholder.markdown(title_placeholder)
        self.show_use_case(self.selected_use_case)

    def show_use_case(self, use_case: str):
        self.use_case_sections = UseCaseSection(use_case, self.use_cases[use_case])
        self.use_case_sections.show()
