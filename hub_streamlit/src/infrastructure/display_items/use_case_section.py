import streamlit as st

from src.infrastructure.cloud_connectors.edge_data import UseCase


# todo: rename use_case_data
class UseCaseSection:
    def __init__(
        self, use_case: str, use_case_data: UseCase, n_cols: int = 5, n_camera: int = 2
    ):
        self.use_case = use_case
        self.use_case_data = use_case_data
        self.n_cols = n_cols
        self.n_camera = n_camera
        self.columns_placeholder = [
            st.columns(self.n_cols) for _ in range(n_camera + 1)
        ]

    def show(self):
        idx_col = 0
        for item_id in self.use_case_data.item_names:
            item = self.use_case_data.items[item_id]
            for idx_camera, camera_id in enumerate(item.camera_names):
                camera_data = item.cameras[camera_id]
                for picture in camera_data.pictures:
                    self.columns_placeholder[idx_camera][idx_col].image(
                        picture, use_container_width=True
                    )

            # Writing some metadata
            self.columns_placeholder[self.n_camera][idx_col].markdown(
                f"<div style='text-align:center; color:grey; font-size:small'>"
                f"{item.creation_date.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Decision: {item.metadata['decision']}</div>",
                unsafe_allow_html=True,
            )

            idx_col += 1

    def empty(self):
        self.columns_placeholder.empty()
