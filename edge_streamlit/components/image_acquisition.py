import threading
import time

import cv2
import streamlit as st
from matplotlib import pyplot as plt
from streamlit_webrtc import webrtc_streamer


def image_acquisition():
    # Initialize session state for images if it doesn't exist
    if "acquired_images" not in st.session_state:
        st.session_state.acquired_images = []

    lock = threading.Lock()
    last_timestamp = {"seconds": None}
    # Use a regular list for the callback
    callback_images = []

    def video_frame_callback(frame):
        number_seconds = 5
        img = frame.to_ndarray(format="bgr24")
        with lock:
            image_obj = {}

            if last_timestamp["seconds"] is None:
                last_timestamp["seconds"] = time.time()

            current_time = time.time()
            if (
                len(callback_images) == 0
                or current_time - last_timestamp["seconds"] >= number_seconds
            ):
                print(f"Acquisition every {number_seconds} seconds")
                last_timestamp["seconds"] = current_time
                image_obj["img"] = img
                callback_images.append(image_obj)

        return frame

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Live Stream")
        ctx = webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

    with col2:
        st.write("### Latest Acquired Image")
        # Create a container for the latest image
        latest_image_container = st.empty()
        fig, ax = plt.subplots(1, 1)

    while ctx.state.playing:
        with lock:
            # Update session state with new images from callback
            if len(callback_images) > len(st.session_state.acquired_images):
                st.session_state.acquired_images = callback_images.copy()

            image = (
                st.session_state.acquired_images[-1]["img"]
                if len(st.session_state.acquired_images) > 0
                else None
            )

        if image is None:
            continue
        print("Image acquisition", len(st.session_state.acquired_images))
        if len(st.session_state.acquired_images) > 0:
            ax.clear()
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            ax.axis("off")
            latest_image_container.pyplot(fig)

    return st.session_state.acquired_images
