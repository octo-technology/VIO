import streamlit as st
from typing import List


def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Init variables
    if "recording" not in st.session_state:
        st.session_state.recording = False

    # Page configuration
    st.set_page_config(
        page_title="Mon Application Streamlit",
        page_icon="🔦",
        layout="wide"
    )

    # Sidebar parameters
    st.sidebar.title("Configuration")
    sidebar()

    # Page content
    st.title("VIO Edge")
    st.markdown("Recording camera 🌐")
    st.write("""
    This application is designed to demonstrate VIO Edge system
    """)

    import cv2
    cap = cv2.VideoCapture(0)
    stframe = st.empty()

    while st.session_state.recording:
        ret, frame = cap.read()
        if not ret:
            st.write("Failed to capture video")
            break

        stframe.image(frame, channels="BGR")
    cap.release()


def sidebar():
    if st.sidebar.button("Start/Stop Recording"):
        st.session_state.recording = not st.session_state.recording

# Exécution du script principal
if __name__ == "__main__":
    main()
