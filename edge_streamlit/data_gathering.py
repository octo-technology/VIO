import json

import requests
import streamlit as st

from components.image_acquisition import image_acquisition
from config import URL_ACTIVE_CONFIG, URL_CONFIGS, URL_ORCH

URL_DATA_UPLOAD = URL_ORCH + "upload"

active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)
if active_config:
    st.session_state.active_config = active_config

if "active_config" not in st.session_state:
    st.session_state.active_config = None
if "data_gathering" not in st.session_state:
    st.session_state.data_gathering = False
if "item_id" not in st.session_state:
    st.session_state.item_id = None
if "class_name" not in st.session_state:
    st.session_state.class_name = "OK"

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
    col3.write("Select a class name")
    st.session_state.class_name = col3.selectbox(
        "Class name",
        ["OK", "NOK"],
        index=0 if st.session_state.class_name == "OK" else 1,
        label_visibility="collapsed",
        help="Select the class name for the images",
    )

st.cache_data.images = image_acquisition()

# Add loading spinner while waiting for response
if st.cache_data.images:
    # only one list of images so we set the camera_id to the first camera
    camera_id = list(st.session_state.active_config.get("camera_configs").keys())[0]
    st.title(f"{len(st.cache_data.images)} images acquired let's upload them")
    with st.spinner("Uploading images..."):
        # Convert numpy arrays to bytes before sending
        files = [('binaries', (camera_id, img.tobytes(), 'image/jpeg')) for img in st.cache_data.images]
        response = requests.post(f"{URL_DATA_UPLOAD}?class_name={st.session_state.class_name}", files=files)
        if response.status_code == 200:
            st.success("Images uploaded successfully!")
        else:
            st.error(f"Failed to upload images. Status code: {response.status_code}")

        st.cache_data.images = None
