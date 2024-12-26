from typing import List
import cv2
import streamlit as st

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
        else:
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