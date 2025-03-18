import io
import json

import requests
import streamlit as st
from PIL import Image

from components.image_acquisition import image_acquisition
from config import URL_ACTIVE_CONFIG, URL_ORCH

URL_DATA_UPLOAD = URL_ORCH + "upload"

# active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)

data_gathering_active_config = "data_gathering"
requests.post(url=f"{URL_ACTIVE_CONFIG}?station_name={data_gathering_active_config}")
st.session_state.active_config = json.loads(requests.get(URL_ACTIVE_CONFIG).text)

st.cache_data.images = image_acquisition()
if "class_name" not in st.session_state:
    st.session_state.class_name = "OK"

col1, col2, col3 = st.columns(3)
# Add loading spinner while waiting for response
if st.cache_data.images:
    # only one list of images so we set the camera_id to the first camera
    camera_id = list(st.session_state.active_config.get("camera_configs").keys())[0]
    st.write(
        f"{len(st.cache_data.images)} images have been acquired, let's upload them"
    )

    st.session_state.class_name = col1.selectbox(
        "Class name",
        ["OK", "NOK"],
        index=0 if st.session_state.class_name == "OK" else 1,
        label_visibility="collapsed",
        help="Select the class name for the images",
    )

    if col2.button("Upload", key="upload", use_container_width=True):
        # Convert numpy arrays to bytes before sending
        files = []
        for img in st.cache_data.images:
            buf = io.BytesIO()
            Image.fromarray(img).save(buf, format="jpeg")
            files.append(("binaries", (camera_id, buf.getvalue(), "image/jpeg")))
        response = requests.post(
            f"{URL_DATA_UPLOAD}?class_name={st.session_state.class_name}", files=files
        )
        if response.status_code == 200:
            col3.success(
                f"Uploaded job launched with label {st.session_state.class_name}"
            )
        else:
            col3.error(f"Failed to upload images. Status code: {response.status_code}")

        st.cache_data.images = None
