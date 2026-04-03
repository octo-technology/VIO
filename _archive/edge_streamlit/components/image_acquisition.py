import threading
import time
from typing import List

import cv2
import numpy as np
import streamlit as st
from matplotlib import pyplot as plt
from streamlit_webrtc import webrtc_streamer

NUMBER_SECONDS = 5


def image_acquisition() -> List[np.ndarray]:
    # Initialize session state for images if it doesn't exist
    if "acquired_images" not in st.session_state:
        st.session_state.acquired_images = []

    lock = threading.Lock()
    last_timestamp = {"seconds": None}
    # Use a regular list for the callback
    callback_images = []
    acquisition_display = {"last_zero": None}

    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        with lock:
            image_obj = {}

            if last_timestamp["seconds"] is None:
                last_timestamp["seconds"] = time.time()

            current_time = time.time()
            if (
                len(callback_images) == 0
                or current_time - last_timestamp["seconds"] >= NUMBER_SECONDS
            ):
                print(f"Acquisition every {NUMBER_SECONDS} seconds")
                last_timestamp["seconds"] = current_time
                image_obj["img"] = img
                callback_images.append(image_obj)

        return frame

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.write("## Live Stream")
        ctx = webrtc_streamer(key="example", video_frame_callback=video_frame_callback)
        # define a timer to display seconds before next acquisition
        timer = st.empty()

    with col2:
        st.write("## Latest Acquired Image")
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

            # Update timer display
            current_time = time.time()
            if last_timestamp["seconds"] is not None:
                time_elapsed = current_time - last_timestamp["seconds"]
                time_remaining = max(0.0, round(NUMBER_SECONDS - time_elapsed, 1))
                if time_remaining <= 0.5:
                    # Only update the last_zero timestamp if we just hit zero
                    if acquisition_display["last_zero"] is None:
                        acquisition_display["last_zero"] = current_time

                    # Show the acquisition message for 3 seconds
                    if current_time - acquisition_display["last_zero"] <= 3.0:
                        timer.markdown(
                            f"<p style='color: green;'>Acquiring an image...</p>",
                            unsafe_allow_html=True,
                        )
                    else:
                        acquisition_display["last_zero"] = None
                else:
                    acquisition_display["last_zero"] = None
                    timer.write(f"Next acquisition in: {time_remaining:.1f} seconds")

        if image is None:
            continue
        print("Image acquisition", len(st.session_state.acquired_images))
        if len(st.session_state.acquired_images) > 0:
            ax.clear()
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            ax.axis("off")
            latest_image_container.pyplot(fig)

    if ctx.state.playing is False:
        if len(st.session_state.acquired_images) > 0:
            image = st.session_state.acquired_images[-1]["img"]
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            ax.axis("off")
            latest_image_container.pyplot(fig)
            timer.write("Stream stopped. Acquisition paused.")

    return [image["img"] for image in st.session_state.acquired_images]
