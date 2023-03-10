import logging
import os

import docker
import pymongo
from _pytest.fixtures import SubRequest
from _pytest.fixtures import fixture
from alembic import command as alembic_command
from alembic.config import Config
from testcontainers.core import config
from testcontainers.core.container import DockerContainer
from testcontainers.mongodb import MongoDbContainer
from testcontainers.postgres import PostgresContainer
from typing import Union, Tuple, Generator, Optional

from tests.conftest import ROOT_REPOSITORY_PATH, EDGE_DB_IMG, HUB_MONITORING_DB_IMG, EDGE_MODEL_SERVING, \
    EDGE_TFLITE_SERVING_IMG
from tests.tf_serving_container import TfServingContainer

config.MAX_TRIES = 5


def check_image_presence_or_pull_it_from_registry(image_name: str):
    client = docker.from_env()
    image_tags = [tag for image in client.images.list() for tag in image.tags]
    if image_name not in image_tags:
        auth_config = None
        logging.info(f'Pulling docker image {image_name} from registry when running tests for the first time...')
        if image_name.startswith('ghcr.io/octo-technology'):
            if os.environ.get('REGISTRY_USERNAME') and os.environ.get('REGISTRY_PASSWORD'):
                auth_config = {'username': os.environ.get('REGISTRY_USERNAME'),
                               'password': os.environ.get('REGISTRY_PASSWORD')}
            else:
                raise PermissionError('Please set your registry credentials with the following env vars: '
                                      'REGISTRY_USERNAME & REGISTRY_PASSWORD')
        client.images.pull(image_name, auth_config=auth_config)


def start_test_db(image_name: str, connection_url: Optional[str]) -> Tuple[str, MongoDbContainer]:
    container = None
    if connection_url is None:
        check_image_presence_or_pull_it_from_registry(image_name)
        if 'mongo' in image_name:
            container = MongoDbContainer(image_name)
        else:
            container = PostgresContainer(image_name)
        container.start()
        connection_url = container.get_connection_url()
    return connection_url, container


def stop_test_container(container: DockerContainer):
    if container:
        container.stop()


@fixture(scope='session')
def setup_test_mongo_db() -> str:
    connection_url, mongo_db_container = start_test_db(image_name=EDGE_DB_IMG,
                                                       connection_url=os.environ.get('MONGO_DB_URI'))
    yield connection_url
    stop_test_container(mongo_db_container)


@fixture(scope='function')
def test_mongo_db_uri(setup_test_mongo_db) -> str:
    yield setup_test_mongo_db
    client = pymongo.MongoClient(setup_test_mongo_db)
    client.drop_database('orchestratorDB')


@fixture(scope='session')
def setup_test_postgres_db() -> str:
    connection_url, postgres_db_container = start_test_db(image_name=HUB_MONITORING_DB_IMG,
                                                          connection_url=os.environ.get('POSTGRES_DB_URI'))
    apply_db_migrations(connection_url)
    yield connection_url
    stop_test_container(postgres_db_container)


@fixture(scope='function')
def test_postgres_db_uri(setup_test_postgres_db) -> str:
    yield setup_test_postgres_db


def start_test_tf_serving(image_name: str, starting_log: str, exposed_model_name: str,
                          tf_serving_host: Union[str, None] = os.environ.get('TENSORFLOW_SERVING_HOST'),
                          tf_serving_port: Union[int, None] = os.environ.get('TENSORFLOW_SERVING_PORT'),
                          host_volume_path: str = None,
                          container_volume_path: str = None) -> Tuple[str, TfServingContainer]:
    container = None
    if tf_serving_host is None or tf_serving_port is None:
        port_to_expose = 8501
        check_image_presence_or_pull_it_from_registry(image_name)
        container = TfServingContainer(image=image_name,
                                       port_to_expose=port_to_expose,
                                       env={'MODEL_NAME': exposed_model_name},
                                       host_volume_path=host_volume_path,
                                       container_volume_path=container_volume_path)
        container.start(starting_log)
        tf_serving_host = container.get_container_host_ip()
        tf_serving_port = container.get_exposed_port(port_to_expose)

    return f'http://{tf_serving_host}:{tf_serving_port}', container


@fixture(scope='session')
def setup_test_tensorflow_serving(request: SubRequest) -> Generator[str, None, None]:
    connection_url, tensorflow_serving_container = start_test_tf_serving(
        image_name=EDGE_MODEL_SERVING['image_name'],
        starting_log=r'Entering the event loop ...',
        exposed_model_name=request.param,
        host_volume_path=((ROOT_REPOSITORY_PATH / EDGE_MODEL_SERVING['host_volume_path_suffix']).as_posix()),
        container_volume_path=EDGE_MODEL_SERVING['container_volume_path']
    )
    yield connection_url
    stop_test_container(tensorflow_serving_container)


@fixture(scope='session')
def setup_test_tflite_serving(request: SubRequest) -> Generator[str, None, None]:
    connection_url, tflite_serving_container = start_test_tf_serving(
        image_name=EDGE_TFLITE_SERVING_IMG,
        starting_log=r'Uvicorn running on',
        exposed_model_name=request.param,
        tf_serving_host=os.environ.get('TFLITE_SERVING_HOST'),
        tf_serving_port=os.environ.get('TFLITE_SERVING_PORT')
    )
    yield connection_url
    stop_test_container(tflite_serving_container)


@fixture(scope='function')
def test_tensorflow_serving_base_url(setup_test_tensorflow_serving) -> str:
    return setup_test_tensorflow_serving


@fixture(scope='function')
def test_tflite_serving_base_url(setup_test_tflite_serving) -> str:
    return setup_test_tflite_serving


def apply_db_migrations(connection_url: str) -> bool:
    os.environ['DB_CONNECTION_URL'] = connection_url
    path_to_migration = ROOT_REPOSITORY_PATH / 'hub_monitoring/db_migrations'
    alembic_cfg = Config(path_to_migration / 'alembic.ini')
    alembic_cfg.set_main_option('script_location', (path_to_migration / 'alembic').as_posix())
    alembic_command.upgrade(alembic_cfg, 'head')
    return True
