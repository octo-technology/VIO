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
        if cap.isOpened():
            available_cameras.append(f"Cam {index}")
        else:
            break
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
