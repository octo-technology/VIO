import os
import sys
import tempfile
from pathlib import Path
from shutil import copytree

from behave.runner import Context
from fastapi.testclient import TestClient

sys.path.append((Path(__file__).parents[1]).resolve().as_posix())

from helpers.container_utils import (
    EDGE_MODEL_SERVING,
    start_test_tf_serving,
    stop_test_container,
)

ROOT_REPOSITORY_PATH = Path(__file__).parents[3]


def before_all(context: Context):
    config_directory = Path(__file__).parents[2] / "config"

    context.tmp_dir = tempfile.TemporaryDirectory()
    test_directory = Path(context.tmp_dir.name)
    context.test_directory = test_directory
    tmp_config_dir = test_directory / "config"

    copytree(config_directory.as_posix(), tmp_config_dir.as_posix())
    active_config_filepath = tmp_config_dir / "active_station_config.json"
    active_config_filepath.unlink(missing_ok=True)

    os.environ["CONFIG_DIR"] = tmp_config_dir.as_posix()
    os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    (
        context.tensorflow_serving_url,
        context.tensorflow_serving_container,
    ) = start_test_tf_serving(
        image_name=EDGE_MODEL_SERVING["image_name"],
        starting_log=r"Entering the event loop ...",
        env_vars={},
        host_volume_path=((ROOT_REPOSITORY_PATH / EDGE_MODEL_SERVING["host_volume_path_suffix"]).as_posix()),
        container_volume_path=EDGE_MODEL_SERVING["container_volume_path"],
    )
    os.environ["SERVING_MODEL_URL"] = context.tensorflow_serving_url
    from edge_orchestrator.interface.api.main import app

    context.test_client = TestClient(app)


def after_all(context: Context):
    context.tmp_dir.cleanup()
    if context.tensorflow_serving_container:
        stop_test_container(context.tensorflow_serving_container)
