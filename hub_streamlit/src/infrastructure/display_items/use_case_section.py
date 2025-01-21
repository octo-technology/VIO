import streamlit as st

from src.infrastructure.data.edge_data import UseCase


# todo: rename use_case_data
class UseCaseSection:
    def __init__(
        self, use_case: str, use_case_data: UseCase, number_cols: int = 5, number_cameras: int = 2
    ):
        self.use_case = use_case
        self.use_case_data = use_case_data
        self.number_cols = number_cols
        self.number_cameras = number_cameras
        self.columns_placeholder = [
            st.columns(self.number_cols) for _ in range(number_cameras + 1)
        ]

    def show(self):
        for idx, item_id in enumerate(self.use_case_data.item_names):
            if idx >= self.number_cols:
                break

            item = self.use_case_data.items[item_id]
            for idx_camera, camera_id in enumerate(item.camera_names):
                camera_data = item.cameras[camera_id]
                for picture in camera_data.pictures:
                    self.columns_placeholder[idx_camera][idx].image(
                        picture, use_container_width=True
                    )

            # Writing some metadata
            self.columns_placeholder[self.number_cameras][idx].markdown(
                f"<div style='text-align:center; color:grey; font-size:small'>"
                f"{item.creation_date.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Decision: {item.metadata['decision']}</div>",
                unsafe_allow_html=True,
            )

    def empty(self):
        self.columns_placeholder.empty()
