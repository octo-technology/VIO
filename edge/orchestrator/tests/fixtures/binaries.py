from pathlib import Path

from pytest import fixture


@fixture(scope="function")
def marker_image() -> bytes:
    source_directory = Path(__file__).resolve().parents[2] / "fake_images"
    with (source_directory / "marker_images" / "10.jpg").open("br") as f:
        return f.read()


@fixture(scope="function")
def people_image() -> bytes:
    source_directory = Path(__file__).resolve().parents[2] / "fake_images"
    with (source_directory / "people_dataset" / "people-1012564545.jpg").open("br") as f:
        return f.read()
