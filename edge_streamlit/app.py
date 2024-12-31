from utils import display_camera_checkboxes, list_cameras
import streamlit as st
import requests
import json

import requests
import streamlit as st

from config import URL_CONFIGS

st.cache_data.configs = json.loads(requests.get(URL_CONFIGS).text)

# Page configuration
st.set_page_config(
    page_title="VIO-edge",
    page_icon="🔦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    pg = st.navigation(
        [
            st.Page(
                "data_gathering.py", title="Data Gathering", icon=":material/bar_chart:"
            ),
            st.Page("trigger.py", title="Trigger", icon=":material/visibility:"),
        ]
    )
    pg.run()


if __name__ == "__main__":
    main()
