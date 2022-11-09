from pathlib import Path

from supervisor.domain.models.edge_station import EdgeStation
from supervisor.environment.config import Config
from supervisor.infrastructure.binary_storage.filesystem_binary_storage import FileSystemBinaryStorage
from supervisor.infrastructure.inventory.json_inventory import JsonInventory
from supervisor.infrastructure.metadata_storage.mongodb_metadata_storage import MongoDbMetadataStorage
from supervisor.infrastructure.model_forward.tf_serving_wrapper import TFServingWrapper
from supervisor.infrastructure.station_config.json_station_config import JsonStationConfig
from supervisor.infrastructure.telemetry_sink.azure_iot_hub_telemetry_sink import AzureIotHubTelemetrySink


class EdgeWithMongoDbMetadataStorage(Config):
    ROOT_PATH = Path('/supervisor')
    SERVING_MODEL_URL = 'http://model_serving:8501'

    def __init__(self):
        self.metadata_storage = MongoDbMetadataStorage('mongodb://mongodb:27017/')
        self.binary_storage = FileSystemBinaryStorage(self.ROOT_PATH / 'data' / 'storage')
        self.inventory = JsonInventory(self.ROOT_PATH / 'config' / 'inventory.json')
        self.station_config = JsonStationConfig(self.ROOT_PATH / 'config' / 'station_configs',
                                                self.inventory, self.ROOT_PATH / 'data')
        self.edge_station = EdgeStation(self.station_config, self.ROOT_PATH / 'data')
        self.model_forward = TFServingWrapper(self.SERVING_MODEL_URL, self.inventory, self.station_config)
        self.telemetry_sink = AzureIotHubTelemetrySink()
