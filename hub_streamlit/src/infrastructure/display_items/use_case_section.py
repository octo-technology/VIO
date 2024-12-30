import streamlit as st


class UseCaseSection:
    def __init__(self, use_case: str, use_case_data: dict, n_cols: int = 5, n_camera: int = 2):
        self.use_case = use_case
        self.use_case_data = use_case_data
        self.n_cols = n_cols
        self.n_camera = n_camera
        self.title_placeholder = st.empty()
        self.columns_placeholder = [st.columns(self.n_cols) for _ in range(n_camera + 1)]

    def show(self):
        self.title_placeholder.markdown(f"##### Use case: {self.use_case.replace('_', ' ').title()}")
        idx_col = 0
        for item_id in self.use_case_data["item_list"]:
            item_data = self.use_case_data[item_id]
            for idx_camera, camera_id in enumerate(item_data["camera_list"]):
                camera_data = item_data[camera_id]
                for picture in camera_data["pictures"]:
                    self.columns_placeholder[idx_camera][idx_col].image(picture, use_container_width=True)

            # Writing some metadata
            self.columns_placeholder[self.n_camera][idx_col].markdown(f"<div style=\'text-align:center; color:grey; font-size:small\'>"
                                                                      f"{item_data['creation_date'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                                                                      f"Decision: {item_data['metadata']['decision']}</div>",
                                                                      unsafe_allow_html=True)

            idx_col += 1

    def empty(self):
        self.title_placeholder.empty()
        self.columns_placeholder.empty()
