import logging
from typing import List

import cv2
import streamlit as st
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"


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
    if len(available_cameras) == 0:
        st.warning("No camera detected.")
    else:
        for i, camera_name in enumerate(available_cameras):
            if st.sidebar.checkbox(camera_name, key=f"camera_{i}"):
                selected_cameras.append(i)
        logger.debug(f"Selected cameras are {selected_cameras}")
    return selected_cameras
