from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.environment.config import Config

from edge_orchestrator.infrastructure.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.inventory.json_inventory import JsonInventory
from edge_orchestrator.infrastructure.metadata_storage.memory_metadata_storage import (
    MemoryMetadataStorage,
)

from edge_orchestrator.infrastructure.model_forward.fake_model_forward import (
    FakeModelForward,
)
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from edge_orchestrator.infrastructure.telemetry_sink.fake_telemetry_sink import (
    FakeTelemetrySink,
)


class Default(Config):
    def __init__(self):
        self.metadata_storage = MemoryMetadataStorage()
        self.model_forward = FakeModelForward()
        self.binary_storage = FileSystemBinaryStorage(
            self.ROOT_PATH / "data" / "storage"
        )
        self.inventory = JsonInventory(self.ROOT_PATH / "config" / "inventory.json")
        self.station_config = JsonStationConfig(
            self.ROOT_PATH / "config" / "station_configs",
            self.inventory,
            self.ROOT_PATH / "data",
        )
        self.edge_station = EdgeStation(self.station_config)
        self.telemetry_sink = FakeTelemetrySink()
