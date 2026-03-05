import os
import time
import urllib.request
from typing import Generator

from helpers.container_utils import (
    EDGE_TFLITE_SERVING_IMG,
    start_test_tf_serving,
    stop_test_container,
)
from pytest import fixture


def _wait_until_ready(url: str, retries: int = 20, delay: float = 1.0) -> None:
    for _ in range(retries):
        try:
            urllib.request.urlopen(f"{url}v1/", timeout=2)
            return
        except Exception:
            time.sleep(delay)
    raise RuntimeError(f"Serving server at {url} did not become ready after {retries}s")


@fixture(scope="session")
def setup_test_tflite_serving() -> Generator[str, None, None]:
    connection_url, tflite_serving_container = start_test_tf_serving(
        image_name=EDGE_TFLITE_SERVING_IMG,
        starting_log=r"Application startup complete",
        env_vars={},
        tf_serving_host=os.getenv("TFLITE_SERVING_HOST"),
        tf_serving_port=os.getenv("TFLITE_SERVING_PORT"),
    )
    if tflite_serving_container is not None:
        _wait_until_ready(connection_url)
    yield connection_url
    stop_test_container(tflite_serving_container)
