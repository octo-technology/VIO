from _pytest.fixtures import fixture

from tests.conftest import EDGE_NAME, TEST_DATA_FOLDER_PATH


@fixture(scope="function")
def my_binaries_0():
    with (TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_0" / "camera_id1.jpg").open("br") as f1, (
        TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_0" / "camera_id2.jpg"
    ).open("br") as f2:
        picture_1 = f1.read()
        picture_2 = f2.read()
    return {"camera_id1": picture_1, "camera_id2": picture_2}


@fixture(scope="function")
def my_binaries_1():
    with (TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_1" / "camera_id1.jpg").open("br") as f:
        picture = f.read()
    return {
        "camera_id1": picture,
        "camera_id2": picture,
        "camera_id3": picture,
        "camera_id4": picture,
    }


@fixture(scope="function")
def my_binaries_2():
    with (TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_2" / "camera_id1.jpg").open("br") as f1, (
        TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_2" / "camera_id2.jpg"
    ).open("br") as f2:
        picture_2 = f1.read()
        picture_3 = f2.read()
    return {"camera_id2": picture_2, "camera_id3": picture_3}


@fixture(scope="function")
def my_fake_binaries():
    with (TEST_DATA_FOLDER_PATH / "fake_item" / "image1.jpg").open("br") as f1, (
        TEST_DATA_FOLDER_PATH / "fake_item" / "image5.jpg"
    ).open("br") as f2, (TEST_DATA_FOLDER_PATH / "fake_item" / "image2.jpg").open("br") as f3, (
        TEST_DATA_FOLDER_PATH / "fake_item" / "image7.jpg"
    ).open(
        "br"
    ) as f4:
        picture_1 = f1.read()
        picture_2 = f2.read()
        picture_3 = f3.read()
        picture_4 = f4.read()
    return {
        "camera_id1": picture_1,
        "camera_id2": picture_2,
        "camera_id3": picture_3,
        "camera_id4": picture_4,
    }


@fixture(scope="function")
def my_fake_binaries_2():
    with (TEST_DATA_FOLDER_PATH / "marker_images" / "160.jpg").open("br") as f:
        picture = f.read()
    return {"camera_id3": picture}
