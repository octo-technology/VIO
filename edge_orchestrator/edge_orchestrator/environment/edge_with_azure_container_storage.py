import os

from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.environment.config import Config
from edge_orchestrator.infrastructure.binary_storage.azure_container_binary_storage import (
    AzureContainerBinaryStorage,
)
from edge_orchestrator.infrastructure.inventory.json_inventory import JsonInventory
from edge_orchestrator.infrastructure.metadata_storage.azure_container_metadata_storage import (
    AzureContainerMetadataStorage,
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


class EdgeWithAzureContainerStorage(Config):
    SERVING_MODEL_URL = os.environ.get("SERVING_MODEL_URL", "http://edge_model_serving:8501")

    def __init__(self):
        self.inventory = JsonInventory(self.ROOT_PATH / "config" / "inventory.json")
        self.station_config = JsonStationConfig(
            self.ROOT_PATH / "config" / "station_configs",
            self.inventory,
            self.ROOT_PATH / "data",
        )
        self.metadata_storage = AzureContainerMetadataStorage(self.station_config.active_config_name)
        self.binary_storage = AzureContainerBinaryStorage(self.station_config.active_config_name)
        self.edge_station = EdgeStation(self.station_config)
        self.model_forward = TFServingWrapper(self.SERVING_MODEL_URL, self.inventory, self.station_config)
        self.telemetry_sink = AzureIotHubTelemetrySink()
