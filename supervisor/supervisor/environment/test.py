import os
from pathlib import Path

from supervisor.domain.models.edge_station import EdgeStation
from supervisor.environment.config import Config
from supervisor.infrastructure.binary_storage.filesystem_binary_storage import FileSystemBinaryStorage
from supervisor.infrastructure.inventory.json_inventory import JsonInventory
from supervisor.infrastructure.metadata_storage.mongodb_metadata_storage import MongoDbMetadataStorage
from supervisor.infrastructure.model_forward.tf_serving_wrapper import TFServingWrapper
from supervisor.infrastructure.station_config.json_station_config import JsonStationConfig
from supervisor.infrastructure.telemetry_sink.fake_telemetry_sink import FakeTelemetrySink
from tests.conftest import TEST_STATION_CONFIGS_FOLDER_PATH, TEST_INVENTORY_PATH, TEST_DATA_FOLDER_PATH


class Test(Config):
    ROOT_PATH = Path('/tests')
    MONGO_DB_URI = os.environ.get('MONGO_DB_URI', 'mongodb://mongodb:27017/')
    SERVING_MODEL_URL = os.environ.get('SERVING_MODEL_URL', 'http://model_serving:8501')

    def __init__(self):
        self.metadata_storage = MongoDbMetadataStorage(self.MONGO_DB_URI)
        self.binary_storage = FileSystemBinaryStorage(TEST_DATA_FOLDER_PATH / 'storage')
        self.inventory = JsonInventory(TEST_INVENTORY_PATH)
        self.station_config = JsonStationConfig(TEST_STATION_CONFIGS_FOLDER_PATH,
                                                self.inventory, TEST_DATA_FOLDER_PATH)
        self.edge_station = EdgeStation(self.station_config, TEST_DATA_FOLDER_PATH)
        self.model_forward = TFServingWrapper(self.SERVING_MODEL_URL, self.inventory, self.station_config)
        self.telemetry_sink = FakeTelemetrySink()
