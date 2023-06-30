from _pytest.fixtures import fixture


@fixture(scope="function")
def right_camera_metadata():
    return {"brightness": 100, "exposition": 100, "position": "right"}


@fixture(scope="function")
def left_camera_metadata():
    return {"brightness": 100, "exposition": 100, "position": "left"}


@fixture(scope="function")
def top_camera_metadata():
    return {"brightness": 100, "exposition": 100, "position": "top"}


@fixture(scope="function")
def bottom_camera_metadata():
    return {"brightness": 100, "exposition": 100, "position": "bottom"}


@fixture(scope="function")
def back_camera_metadata():
    return {
        "brightness": None,
        "exposition": 100,
        "position": "back",
        "source": "marker_images",
    }
