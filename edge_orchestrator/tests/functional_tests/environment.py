import os
from pathlib import Path
from shutil import rmtree

from behave.runner import Context
from fastapi.testclient import TestClient

from tests.conftest import (
    EDGE_MODEL_SERVING,
)
from tests.fixtures.containers import (
    start_test_tf_serving,
    stop_test_container,
)

ROOT_REPOSITORY_PATH = Path(__file__).parents[3]
TEST_DATA_FOLDER_PATH = Path(__file__).parents[2]/ "data_storage"

def before_all(context: Context):
    context.test_directory = Path(__file__).parent.parent
    (
        context.tensorflow_serving_url,
        context.tensorflow_serving_container,
    ) = start_test_tf_serving(
        image_name=EDGE_MODEL_SERVING["image_name"],
        starting_log=r"Entering the event loop ...",
        exposed_model_name="marker_quality_control",
        host_volume_path=((ROOT_REPOSITORY_PATH / EDGE_MODEL_SERVING["host_volume_path_suffix"]).as_posix()),
        container_volume_path=EDGE_MODEL_SERVING["container_volume_path"],
    )
    os.environ["SERVING_MODEL_URL"] = context.tensorflow_serving_url
    from edge_orchestrator.interface.api.main import app

    context.test_client = TestClient(app)


def after_all(context: Context):
    rmtree(TEST_DATA_FOLDER_PATH / "storage")
    if context.tensorflow_serving_container:
        stop_test_container(context.tensorflow_serving_container)
