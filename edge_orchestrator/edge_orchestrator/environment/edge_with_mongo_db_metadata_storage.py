import os

from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.environment.config import Config
from edge_orchestrator.infrastructure.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.inventory.json_inventory import JsonInventory
from edge_orchestrator.infrastructure.metadata_storage.mongodb_metadata_storage import (
    MongoDbMetadataStorage,
)
from edge_orchestrator.infrastructure.model_forward.tf_serving_wrapper import (
    TFServingWrapper,
)
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from edge_orchestrator.infrastructure.telemetry_sink.azure_iot_hub_telemetry_sink import (
    AzureIotHubTelemetrySink,
)


class EdgeWithMongoDbMetadataStorage(Config):
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb://edge_db:27017/")
    SERVING_MODEL_URL = os.environ.get("SERVING_MODEL_URL", "http://edge_model_serving:8501")

    def __init__(self):
        self.metadata_storage = MongoDbMetadataStorage(self.MONGO_DB_URI)
        self.binary_storage = FileSystemBinaryStorage(self.ROOT_PATH / "data" / "storage")
        self.inventory = JsonInventory(self.ROOT_PATH / "config" / "inventory.json")
        self.station_config = JsonStationConfig(
            self.ROOT_PATH / "config" / "station_configs",
            self.inventory,
            self.ROOT_PATH / "data",
        )
        self.edge_station = EdgeStation(self.station_config)
        self.model_forward = TFServingWrapper(self.SERVING_MODEL_URL, self.inventory, self.station_config)
        self.telemetry_sink = AzureIotHubTelemetrySink()
