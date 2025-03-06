import streamlit as st

# Page configuration
st.set_page_config(page_title="VIO-edge", page_icon="🔦", layout="wide")


def main():
    pg = st.navigation(
        [
            st.Page("trigger.py", title="Trigger", icon=":material/visibility:"),
            st.Page(
                "data_gathering.py", title="Data Gathering", icon=":material/bar_chart:"
            ),
        ]
    )
    pg.run()


if __name__ == "__main__":
    main()
