from utils import display_camera_checkboxes, list_cameras
import streamlit as st
import requests
import json
import cv2

# Page configuration
st.set_page_config(
    page_title="Mon Application Streamlit",
    page_icon="🔦",
    layout="wide"
)

# Page content
st.title("VIO Edge")

URL_ORCH = "http://localhost:8000/api/v1/"
url_config = URL_ORCH + "configs"
url_active_config = URL_ORCH + "configs/active"
url_trigger = URL_ORCH + "trigger"

def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Init variables
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "selected_cameras" not in st.session_state:
        st.session_state.selected_cameras = []
    if "trigger" not in st.session_state:
        st.session_state.trigger = False
    if "image" not in st.session_state:
        st.session_state.image = None
        
    col_1, col_2 = st.columns(2)

    configs = json.loads(requests.get(url_config).text)

    option = col_1.selectbox("Select an option", tuple(configs), label_visibility="collapsed")

    if col_2.button("Active Config"):
        body = {
            "config_name": option
        }
        requests.post(url=url_active_config, json=body)
        active_config = None
        active_config = json.loads(requests.get(url_active_config).text).get("name")
        col_2.write(f"active config: {active_config}" )

    # Sidebar parameters
    st.sidebar.title("Configuration")
    available_cameras = list_cameras()
    selected_cameras = display_camera_checkboxes(available_cameras)
    st.session_state.selected_cameras = selected_cameras

    if st.sidebar.button("Start/Stop Recording"):
        st.session_state.recording = not st.session_state.recording

    if st.button("Trigger"):
        st.session_state.trigger = True
        response = requests.post(url_trigger)
        item_id = response.json().get("item_id")
        st.subheader(item_id)

    # Video capture logic
    if st.session_state.recording and selected_cameras:
        caps = {index: cv2.VideoCapture(index) for index in selected_cameras}
        columns = st.columns(len(selected_cameras))
        frames_video = {index: columns[i].empty() for i, index in enumerate(selected_cameras)}

        while st.session_state.recording:
            for index in selected_cameras:
                ret, frame = caps[index].read()
                if st.session_state.trigger:
                    st.session_state.image = frame
                    
                if ret:
                    frames_video[index].image(frame, channels="BGR")
                else:
                    frames_video[index].text(f"Camera {index} - Failed to capture video")

                if st.session_state.image is not None and st.session_state.trigger:
                    columns[index].image(st.session_state.image , channels="BGR")
                    # Convertir le tableau NumPy en bytes
                    # _, buffer = cv2.imencode('.jpg', st.session_state.image)
                    # img_byte_arr = BytesIO(buffer)
                    # response = requests.post(url_trigger, files={"image": ("filename", img_byte_arr, "image/jpeg")})
                    # print(response.text)
                    # columns[index].write(response.text)

            st.session_state.trigger = False

        for cap in caps.values():
            cap.release()




# Exécution du script principal
if __name__ == "__main__":
    main()
