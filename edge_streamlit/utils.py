import logging
from typing import List
import cv2
import streamlit as st


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def list_cameras() -> List[str]:
    """
    Liste toutes les caméras disponibles sur le système.
    """
    logger.info("Listing available cameras")
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
    logger.debug(f"{len(available_cameras)} cameras found")
    return available_cameras


def display_camera_checkboxes(available_cameras: List[str]) -> List[int]:
    """
    Affiche les caméras disponibles sous forme de cases à cocher.
    Retourne les indices des caméras sélectionnées.
    """
    selected_cameras = []
    if len(available_cameras) == 0:
        st.warning("No camera detected.")
    else:
        for i, camera_name in enumerate(available_cameras):
            if st.sidebar.checkbox(camera_name, key=f"camera_{i}"):
                selected_cameras.append(i)
        logger.debug(f"Selected cameras are {selected_cameras}")
    return selected_cameras
