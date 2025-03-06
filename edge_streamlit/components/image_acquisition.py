
import streamlit as st


def image_acquisition():
    picture = st.camera_input("Take a picture")

    if picture:
        st.image(picture)
        st.write("Picture taken!")