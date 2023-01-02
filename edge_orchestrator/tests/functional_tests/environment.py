import os
from pathlib import Path
from shutil import rmtree

from behave.runner import Context
from fastapi.testclient import TestClient

from tests.conftest import ROOT_REPOSITORY_PATH, TEST_DATA_FOLDER_PATH, EDGE_DB_IMG, EDGE_MODEL_SERVING_IMG
from tests.fixtures.containers import start_test_mongo_db, start_test_tf_serving, stop_test_container


def before_all(context: Context):
    context.test_directory = Path(__file__).parent.parent
    image_name = EDGE_DB_IMG
    context.mongo_db_uri, context.mongo_db_container = start_test_mongo_db(image_name=image_name)
    image_name = EDGE_MODEL_SERVING_IMG
    context.tensorflow_serving_url, context.tensorflow_serving_container = start_test_tf_serving(
        image_name=image_name,
        starting_log=r'Entering the event loop ...',
        exposed_model_name="marker_quality_control",
        host_volume_path=((ROOT_REPOSITORY_PATH / 'edge_model_serving').as_posix()),
        container_volume_path='/models')
    os.environ['API_CONFIG'] = 'test'
    os.environ['MONGO_DB_URI'] = context.mongo_db_uri
    os.environ['SERVING_MODEL_URL'] = context.tensorflow_serving_url
    from edge_orchestrator.application.server import server
    context.test_client = TestClient(server())


def after_all(context: Context):
    rmtree(TEST_DATA_FOLDER_PATH / 'storage')
    if context.mongo_db_container:
        stop_test_container(context.mongo_db_container)
    if context.tensorflow_serving_container:
        stop_test_container(context.tensorflow_serving_container)
