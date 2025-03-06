import os
import shutil
import sys
import tempfile
from pathlib import Path
from shutil import copytree

from behave.runner import Context
from fastapi.testclient import TestClient

sys.path.append((Path(__file__).parents[1]).resolve().as_posix())
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

from helpers.container_utils import (  # EDGE_MODEL_SERVING,
    EDGE_TFLITE_SERVING_IMG,
    start_test_tf_serving,
    stop_test_container,
)

ROOT_REPOSITORY_PATH = Path(__file__).parents[3]


def before_all(context: Context):
    config_directory = Path(__file__).parents[1] / "config"

    context.tmp_dir = tempfile.TemporaryDirectory()
    test_directory = Path(context.tmp_dir.name)
    context.test_directory = test_directory
    tmp_config_dir = test_directory / "config"

    copytree(config_directory.as_posix(), tmp_config_dir.as_posix())

    os.environ["CONFIG_DIR"] = tmp_config_dir.as_posix()
    os.environ["ACTIVE_CONFIG_NAME"] = "unknown_config"
    (
        model_serving_url,
        context.tensorflow_serving_container,
    ) = start_test_tf_serving(
        image_name=EDGE_TFLITE_SERVING_IMG,
        starting_log=r"Application startup complete.",
        env_vars={},
        tf_serving_host=os.getenv("TFLITE_SERVING_HOST"),
        tf_serving_port=os.getenv("TFLITE_SERVING_PORT"),
    )
    from edge_orchestrator.interface.api.main import app

    context.test_client = TestClient(app)

    from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager

    StoringPathManager.get_storing_prefix_path = lambda x: test_directory / "data_storage"

    from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
        IModelForwarder,
    )

    IModelForwarder._build_model_url = (
        lambda self, base_url, model_name, model_version: f"{model_serving_url}v1/models/{model_name}/versions/{model_version}:predict"
    )


def after_scenario(context: Context, scenario):
    storing_path = Path(context.tmp_dir.name) / "data_storage"
    if storing_path.exists():
        shutil.rmtree(storing_path)
        storing_path.mkdir()


def after_all(context: Context):
    context.tmp_dir.cleanup()
    if context.tensorflow_serving_container:
        stop_test_container(context.tensorflow_serving_container)
