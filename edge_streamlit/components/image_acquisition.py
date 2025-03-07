
import streamlit as st

import threading

import cv2
import streamlit as st
from matplotlib import pyplot as plt

from streamlit_webrtc import webrtc_streamer
import av
import time


def image_acquisition():
    
    lock = threading.Lock()
    images = []
    last_timestamp = {"seconds": None}

    def video_frame_callback(frame):
        number_seconds = 5
        img = frame.to_ndarray(format="bgr24")
        with lock:
            # print("img_container", img_container)
            # print("last_timestamp", last_seconds["seconds"])
            image_obj = {}

            if last_timestamp["seconds"] is None:
                last_timestamp["seconds"] = time.time()
            # print("last_timestamp", last_seconds["seconds"])

            current_time = time.time()
            # print("current_time", current_time)
            # print("current_time - last_timestamp", current_time - last_seconds["seconds"] >= number_seconds)
            if len(images) == 0 or current_time - last_timestamp["seconds"] >= number_seconds:
                print(f"Acquisition every {number_seconds} seconds")
                last_timestamp["seconds"] = current_time
                image_obj["img"] = img
            
                images.append(image_obj)

        return frame


    ctx = webrtc_streamer(key="example", video_frame_callback=video_frame_callback)


    fig_place = st.empty()
    fig, ax = plt.subplots(1, 1)

    while ctx.state.playing:
        with lock:
            image = images[-1]["img"] if len(images) > 0 else None

        if image is None:
            continue
        print("Image acquisition", len(images))
        if len(images) > 0:
            ax.clear()
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            ax.axis('off')
            fig_place.pyplot(fig)

    # if len(images) > 0:
    #     st.write("Image acquisition")
    #     for img_obj in images:
    #         st.image(img_obj["img"], channels="BGR")