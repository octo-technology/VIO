from edge_orchestrator.environment.config import Config
from edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage import GCPBinaryStorage
from edge_orchestrator.infrastructure.metadata_storage.gcp_metadata_storage import GCPMetadataStorage
from edge_orchestrator.infrastructure.inventory.json_inventory import JsonInventory
from edge_orchestrator.infrastructure.station_config.json_station_config import JsonStationConfig
from edge_orchestrator.infrastructure.model_forward.fake_model_forward import FakeModelForward
from edge_orchestrator.infrastructure.telemetry_sink.fake_telemetry_sink import FakeTelemetrySink


class UploadWithGCPBucket(Config):

    def __init__(self):
        self.metadata_storage = GCPMetadataStorage()
        self.binary_storage = GCPBinaryStorage()
        self.inventory = JsonInventory(self.ROOT_PATH / 'config' / 'inventory.json')
        self.station_config = JsonStationConfig(self.ROOT_PATH / 'config' / 'station_configs',
                                                self.inventory, self.ROOT_PATH / 'data')
        self.model_forward = FakeModelForward()
        self.telemetry_sink = FakeTelemetrySink()
