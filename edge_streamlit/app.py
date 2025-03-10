import streamlit as st

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
