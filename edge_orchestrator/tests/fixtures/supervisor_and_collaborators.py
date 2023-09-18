import os
from pathlib import Path

from _pytest.fixtures import fixture

from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.domain.use_cases.supervisor import Supervisor
from edge_orchestrator.infrastructure.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.mongo_db_metadata_storage import (
    MongoDbMetadataStorage,
)
from edge_orchestrator.infrastructure.model_forward.tf_serving_wrapper import (
    TFServingWrapper,
)
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from edge_orchestrator.infrastructure.telemetry_sink.postgres_telemetry_sink import (
    PostgresTelemetrySink,
)
from tests.conftest import (
    TEST_DATA_FOLDER_PATH,
    TEST_STATION_CONFIGS_FOLDER_PATH,
)

ROOT_PATH = Path("/tests")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb://edge_db:27017/")
POSTGRES_DB_URI = os.environ.get(
    "POSTGRES_DB_URI", "postgresql://vio:vio@hub_monitoring_db:5432/vio"
)
SERVING_MODEL_URL = os.environ.get(
    "SERVING_MODEL_URL", "http://edge_model_serving:8501"
)


@fixture(scope="function")
def mongodb_metadata_storage():
    return MongoDbMetadataStorage(MONGO_DB_URI)


@fixture(scope="function")
def filesystem_binary_storage():
    return FileSystemBinaryStorage(TEST_DATA_FOLDER_PATH / "storage")


@fixture(scope="function")
def json_station_config(json_inventory):
    return JsonStationConfig(TEST_STATION_CONFIGS_FOLDER_PATH, TEST_DATA_FOLDER_PATH)


@fixture(scope="function")
def edge_station(json_station_config):
    return EdgeStation(json_station_config)


@fixture(scope="function")
def tf_model_forward():
    return TFServingWrapper(SERVING_MODEL_URL)


@fixture(scope="function")
def postgres_telemetry_sink():
    return PostgresTelemetrySink(POSTGRES_DB_URI)


@fixture(scope="function")
def postgres_telemetry_sink():
    return PostgresTelemetrySink(POSTGRES_DB_URI)


@fixture(scope="function")
def supervisor(
    filesystem_binary_storage,
    edge_station,
    mongodb_metadata_storage,
    tf_model_forward,
    json_station_config,
    postgres_telemetry_sink,
):
    return Supervisor(
        filesystem_binary_storage,
        edge_station,
        mongodb_metadata_storage,
        tf_model_forward,
        json_station_config,
        postgres_telemetry_sink,
    )
