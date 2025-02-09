import os
from pathlib import Path
from shutil import rmtree

from behave.runner import Context
from fastapi.testclient import TestClient

from tests.conftest import (
    EDGE_DB_IMG,
    EDGE_MODEL_SERVING,
    HUB_MONITORING_DB_IMG,
    ROOT_REPOSITORY_PATH,
    TEST_DATA_FOLDER_PATH,
)
from tests.fixtures.containers import (
    apply_db_migrations,
    start_test_db,
    start_test_tf_serving,
    stop_test_container,
)


def before_all(context: Context):
    context.test_directory = Path(__file__).parent.parent
    context.mongo_db_uri, context.mongo_db_container = start_test_db(
        image_name=EDGE_DB_IMG, connection_url=os.environ.get("MONGO_DB_URI")
    )
    context.postgres_db_uri, context.postgres_db_container = start_test_db(
        image_name=HUB_MONITORING_DB_IMG,
        connection_url=os.environ.get("POSTGRES_DB_URI"),
    )
    apply_db_migrations(context.postgres_db_uri)

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
    os.environ["API_CONFIG"] = "test"
    os.environ["MONGO_DB_URI"] = context.mongo_db_uri
    os.environ["POSTGRES_DB_URI"] = context.postgres_db_uri
    os.environ["SERVING_MODEL_URL"] = context.tensorflow_serving_url
    from edge_orchestrator.application.server import server

    context.test_client = TestClient(server())


def after_all(context: Context):
    rmtree(TEST_DATA_FOLDER_PATH / "storage")
    if context.mongo_db_container:
        stop_test_container(context.mongo_db_container)
    if context.postgres_db_container:
        stop_test_container(context.postgres_db_container)
    if context.tensorflow_serving_container:
        stop_test_container(context.tensorflow_serving_container)
