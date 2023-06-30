from _pytest.fixtures import fixture


@fixture(scope="function")
def my_cameras_metadata_0(right_camera_metadata, left_camera_metadata):
    return {"camera_1": right_camera_metadata, "camera_2": left_camera_metadata}


@fixture(scope="function")
def my_cameras_metadata_1(
    right_camera_metadata,
    left_camera_metadata,
    top_camera_metadata,
    bottom_camera_metadata,
):
    return {
        "camera_id1": right_camera_metadata,
        "camera_id2": left_camera_metadata,
        "camera_id3": top_camera_metadata,
        "camera_id4": bottom_camera_metadata,
    }


@fixture(scope="function")
def my_cameras_metadata_2(top_camera_metadata):
    return {"camera_3": top_camera_metadata}


@fixture(scope="function")
def my_cameras_metadata_3(back_camera_metadata):
    return {"camera_id3": back_camera_metadata}
