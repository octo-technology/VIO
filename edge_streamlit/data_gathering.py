import json
import time
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

from config import URL_ACTIVE_CONFIG, URL_CONFIGS, URL_ORCH
from components.image_acquisition import image_acquisition
from prediction_boxes import camera_id_been_pinged

URL_DATA_GATHERING = URL_ORCH + "data_gathering"

active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)
if active_config:
    st.session_state.active_config = active_config

if "active_config" not in st.session_state:
    st.session_state.active_config = None
if "data_gathering" not in st.session_state:
    st.session_state.data_gathering = False
if "item_id" not in st.session_state:
    st.session_state.item_id = None

col1, col2, col3 = st.columns(3)

configs = json.loads(requests.get(URL_CONFIGS).text)

active_config_index = 0
if st.session_state.active_config:
    active_station_name = st.session_state.active_config.get("station_name")
    active_config_index = next(
        (
            index
            for (index, config) in enumerate(configs.values())
            if config["station_name"] == active_station_name
        ),
        0,
    )
selected_station_name = col1.selectbox(
    "Select an option",
    tuple(configs),
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
    if col3.button("Data gathering", use_container_width=True):
        st.session_state.data_gathering = True
        response = requests.post(URL_DATA_GATHERING)
        item_id = response.json().get("item_id")
        st.session_state.item_id = item_id
        col3.write(f"item id: {item_id}")

    # Dropdown to select a class name
    st.write("Select a class name")
    class_name = st.selectbox(
        "Select an option",
        ["OK", "NOK"],
        index=0,
        label_visibility="collapsed",
    )

image_acquisition()

columns = st.columns(2)

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
    for i, camera_id in enumerate(cameras):
        url_binaries = (
            URL_ORCH + f"items/{st.session_state.item_id}/binaries/{camera_id}"
        )
        response = requests.get(url_binaries)
        image = response.content
        # If metadata is not empty, we plot the predictions
        camera_id_has_been_pinged = camera_id_been_pinged(metadata, camera_id)
        if not camera_id_has_been_pinged:
            columns[i].info(f"No ping found for camera {camera_id}")
        else:
            if camera_id_has_been_pinged:
                image = Image.open(BytesIO(image))
            columns[i].image(image, channels="BGR", width=450)
            if inferences.get(camera_id):
                columns[i].markdown(inferences[camera_id])

    st.markdown(
        f"<h1 style='text-align: center; color: #e67e22;'>{decision}</h1>",
        unsafe_allow_html=True,
    )
