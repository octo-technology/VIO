import streamlit as st
from typing import List
import cv2
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Mon Application Streamlit",
    page_icon="🔦",
    layout="wide"
)

URL_ORCH = "http://localhost:8000/api/v1/"
url_config = URL_ORCH + "configs/active"

def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Init variables
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "selected_cameras" not in st.session_state:
        st.session_state.selected_cameras = []
    col_1, col_2 = st.columns(2)
    if col_1.button("Active"):
        body = {
  "config_name": "marker_classification_with_1_fake_camera"
}
        requests.post(url=url_config, json=body)

    active_config = None
    active_config = json.loads(requests.get(url_config).text).get("name")
    col_2.write(f"active config: {active_config}" )

    # Sidebar parameters
    st.sidebar.title("Configuration")
    available_cameras = list_cameras()
    selected_cameras = display_camera_checkboxes(available_cameras)
    st.session_state.selected_cameras = selected_cameras

    if st.sidebar.button("Start/Stop Recording"):
        st.session_state.recording = not st.session_state.recording

    # Page content
    st.title("VIO Edge")
    st.markdown("Recording cameras 🌐")
    st.write("""
    This application is designed to demonstrate VIO Edge system with multiple camera feeds.
    """)

    # Video capture logic
    if st.session_state.recording and selected_cameras:
        capture_videos(selected_cameras)


def list_cameras() -> List[str]:
    """
    Liste toutes les caméras disponibles sur le système.
    """
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        available_cameras.append(f"Cam {index}")
        cap.release()
        index += 1
    return available_cameras


def display_camera_checkboxes(available_cameras: List[str]) -> List[int]:
    """
    Affiche les caméras disponibles sous forme de cases à cocher.
    Retourne les indices des caméras sélectionnées.
    """
    selected_cameras = []
    for i, camera_name in enumerate(available_cameras):
        if st.sidebar.checkbox(camera_name, key=f"camera_{i}"):
            selected_cameras.append(i)
    return selected_cameras


def capture_videos(selected_cameras: List[int]):
    """
    Capture et affiche les flux vidéo des caméras sélectionnées.
    """
    caps = {index: cv2.VideoCapture(index) for index in selected_cameras}
    columns = st.columns(len(selected_cameras))
    frames = {index: columns[i].empty() for i, index in enumerate(selected_cameras)}

    while st.session_state.recording:
        for index in selected_cameras:
            ret, frame = caps[index].read()
            if ret:
                frames[index].image(frame, channels="BGR")
            else:
                frames[index].text(f"Camera {index} - Failed to capture video")

    for cap in caps.values():
        cap.release()



# Exécution du script principal
if __name__ == "__main__":
    main()
