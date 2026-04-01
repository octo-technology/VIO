import json
import time
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

from config import URL_ACTIVE_CONFIG, URL_ORCH
from prediction_boxes import camera_id_been_pinged

URL_TRIGGER = URL_ORCH + "trigger"

active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)
if active_config:
    st.session_state.active_config = active_config

if "active_config" not in st.session_state:
    st.session_state.active_config = None
if "trigger" not in st.session_state:
    st.session_state.trigger = False
if "item_id" not in st.session_state:
    st.session_state.item_id = None

col1, col2, col3 = st.columns(3)

active_config_index = 0
if st.session_state.active_config:
    active_station_name = st.session_state.active_config.get("station_name")
    active_config_index = next(
        (
            index
            for (index, config) in enumerate(st.cache_data.configs.values())
            if config["station_name"] == active_station_name
        ),
        0,
    )
selected_station_name = col1.selectbox(
    "Select an option",
    tuple(st.cache_data.configs),
    index=active_config_index,
    label_visibility="collapsed",
)

if col2.button("Active", use_container_width=True):
    st.session_state.item_id = None
    requests.post(url=f"{URL_ACTIVE_CONFIG}?station_name={selected_station_name}")
    st.session_state.active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)

if st.session_state.active_config:
    active_station_name = st.session_state.active_config.get("station_name")
    col2.write(f"active config name: {active_station_name}")

if st.session_state.active_config:
    if col3.button("Trigger", use_container_width=True):
        st.session_state.trigger = True
        response = requests.post(URL_TRIGGER)
        item_id = response.json().get("item_id")
        st.session_state.item_id = item_id
        col3.write(f"item id: {item_id}")

number_cameras = len(st.session_state.active_config["camera_configs"].keys())
number_columns = number_cameras * 2 + 1
columns = st.columns(number_columns)
odd_numbers = [idx for idx in range(1, number_columns, 2)]

if st.session_state.item_id and (st.session_state.active_config is not None):
    time.sleep(5)

    url_metadata = URL_ORCH + f"items/{st.session_state.item_id}"
    response = requests.get(url_metadata)
    metadata = response.json()
    decision = metadata.get("decision")
    inferences = metadata.get("predictions")

    print("decision", decision)
    print("inferences", inferences)

    camera_configs = st.session_state.active_config.get("camera_configs")
    if not camera_configs:
        st.write("No camera configurations found")
        st.stop()

    cameras = list(camera_configs.keys())
    for idx, camera_id in enumerate(cameras):
        odd_idx = odd_numbers[idx]
        url_binaries = (
            URL_ORCH + f"items/{st.session_state.item_id}/binaries/{camera_id}"
        )
        response = requests.get(url_binaries)
        image = response.content
        # If metadata is not empty, we plot the predictions
        camera_id_has_been_pinged = camera_id_been_pinged(metadata, camera_id)
        if not camera_id_has_been_pinged:
            columns[odd_idx].info(f"No ping found for camera with id : {camera_id}")
        else:
            if camera_id_has_been_pinged:
                image = Image.open(BytesIO(image))
            columns[odd_idx].image(image, channels="BGR")
            if inferences.get(camera_id):
                inference = inferences[camera_id]
                columns[odd_idx].markdown(
                    f"<div style='text-align:center; color:grey; font-size:x-large'>"
                    f"Label: <b>{inference.get('label')}</b><br>"
                    f"Probability: <b>{inference.get('probability')}</b></div>",
                    unsafe_allow_html=True,
                )

    color = "green" if decision == "OK" else "red"
    st.markdown(
        f"<div style='text-align:center; color:{color}; font-size:x-large'>"
        f"Decision: <b>{decision}</b><br>",
        unsafe_allow_html=True,
    )
