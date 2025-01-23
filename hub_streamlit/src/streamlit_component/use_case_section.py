import streamlit as st

from models.use_case import UseCase


class UseCaseSection:
    def __init__(
        self,
        use_case_name: str,
        use_case: UseCase,
        number_cols: int = 8,
        number_cameras: int = 2,
    ):
        self.use_case = use_case_name
        self.use_case = use_case
        self.number_cols = number_cols
        self.number_cameras = number_cameras
        self.columns_placeholder = [
            st.columns(self.number_cols) for _ in range(number_cameras + 1)
        ]

    def show(self):
        for idx, item_id in enumerate(self.use_case.get_item_ids()):
            if idx >= self.number_cols:
                break

            item = self.use_case.get_item(item_id)
            for camera_idx, camera_id in enumerate(item.camera_names):
                camera_data = item.cameras[camera_id]
                for picture in camera_data.pictures:
                    self.columns_placeholder[camera_idx][idx].image(
                        picture, use_container_width=True
                    )

            # Writing some metadata
            self.columns_placeholder[self.number_cameras][idx].markdown(
                f"<div style='text-align:center; color:grey; font-size:small'>"
                f"{item.creation_date.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Decision: {item.metadata.get('decision')}</div>",
                unsafe_allow_html=True,
            )

    def empty(self):
        self.columns_placeholder.empty()
