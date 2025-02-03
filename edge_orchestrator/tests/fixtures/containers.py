import os
from typing import Generator

from conftest import EDGE_TFLITE_SERVING_IMG
from helpers.container_utils import start_test_tf_serving, stop_test_container
from pytest import fixture


@fixture(scope="session")
def setup_test_tflite_serving() -> Generator[str, None, None]:
    connection_url, tflite_serving_container = start_test_tf_serving(
        image_name=EDGE_TFLITE_SERVING_IMG,
        starting_log=r"Uvicorn running on",
        env_vars={},
        tf_serving_host=os.environ.get("TFLITE_SERVING_HOST"),
        tf_serving_port=os.environ.get("TFLITE_SERVING_PORT"),
    )
    yield connection_url
    stop_test_container(tflite_serving_container)
