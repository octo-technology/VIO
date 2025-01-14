import json
import os
import time
import requests
import streamlit as st
from prediction_boxes import filtering_items_that_have_predictions, plot_predictions
from PIL import Image
from io import BytesIO
from utils import display_camera_checkboxes, list_cameras
import cv2

# Page configuration
st.set_page_config(page_title="VIO-edge", page_icon="🔦", layout="wide")

URL_ORCH = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/v1/")

url_config = URL_ORCH + "configs"
url_active_config = URL_ORCH + "configs/active"
url_trigger = URL_ORCH + "trigger"


def main():
    active_config = json.loads(requests.get(url_active_config).text)
    if active_config:
        st.session_state.active_config = active_config

    if "active_config" not in st.session_state:
        st.session_state.active_config = None
    if "trigger" not in st.session_state:
        st.session_state.trigger = False
    if "item_id" not in st.session_state:
        st.session_state.item_id = None
    if "recording" not in st.session_state:
        st.session_state.recording = None

    col1, col2, col3 = st.columns(3)

    configs = json.loads(requests.get(url_config).text)

    active_config_index = 0
    if st.session_state.active_config:
        active_config_name = st.session_state.active_config.get("name")
        active_config_index = next(
            (
                index
                for (index, config) in enumerate(configs.values())
                if config["name"] == active_config_name
            ),
            0,
        )
    option = col1.selectbox(
        "Select an option",
        tuple(configs),
        index=active_config_index,
        label_visibility="collapsed",
    )

    if col2.button("Active", use_container_width=True):
        st.session_state.item_id = None
        body = {"config_name": option}
        requests.post(url=url_active_config, json=body)
        st.session_state.active_config = json.loads(
            requests.get(url_active_config).text
        )

    if st.session_state.active_config:
        active_config_name = st.session_state.active_config.get("name")
        col2.write(f"active config: {active_config_name}")

    if st.session_state.active_config:
        if col3.button("Trigger", use_container_width=True):
            st.session_state.trigger = True
            response = requests.post(url_trigger)
            item_id = response.json().get("item_id")
            st.session_state.item_id = item_id
            col3.write(f"item id: {item_id}")

    columns = st.columns(2)

    if st.session_state.item_id and (st.session_state.active_config is not None):
        time.sleep(5)

        url_metadata = URL_ORCH + f"items/{st.session_state.item_id}"
        response = requests.get(url_metadata)
        metadata = response.json()
        decision = metadata["decision"]
        inferences = metadata["inferences"]

        print("decision", decision)
        print("inferences", inferences)

        cameras = st.session_state.active_config["cameras"]
        for i, camera in enumerate(cameras):
            url_binaries = (
                URL_ORCH + f"items/{st.session_state.item_id}/binaries/{camera}"
            )
            response = requests.get(url_binaries)
            image = response.content
            # If metadata is not empty, we plot the predictions
            if filtering_items_that_have_predictions(metadata, camera):
                image = Image.open(BytesIO(image))
                image = plot_predictions(image, camera, metadata)
            columns[i].image(image, channels="BGR", width=450)
            if inferences.get(camera):
                columns[i].markdown(inferences[camera])

        st.markdown(
            f"<h1 style='text-align: center; color: #e67e22;'>{decision}</h1>",
            unsafe_allow_html=True,
        )

    # Sidebar parameters
    st.sidebar.title("Configuration")
    available_cameras = list_cameras()
    selected_cameras = display_camera_checkboxes(available_cameras)
    st.session_state.selected_cameras = selected_cameras

    if st.sidebar.button("Start/Stop Recording"):
        st.session_state.recording = not st.session_state.recording

    # Video capture logic
    if st.session_state.recording and selected_cameras:
        caps = {index: cv2.VideoCapture(index) for index in selected_cameras}
        columns = st.columns(len(selected_cameras))
        frames_video = {
            index: columns[i].empty() for i, index in enumerate(selected_cameras)
        }

        while st.session_state.recording:
            for index in selected_cameras:
                ret, frame = caps[index].read()
                if st.session_state.trigger:
                    st.session_state.image = frame

                if ret:
                    frames_video[index].image(frame, channels="BGR")
                else:
                    frames_video[index].text(
                        f"Camera {index} - Failed to capture video"
                    )


if __name__ == "__main__":
    main()
