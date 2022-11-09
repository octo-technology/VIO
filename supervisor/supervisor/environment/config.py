from pathlib import Path

from supervisor.domain.models.edge_station import EdgeStation
from supervisor.domain.ports.binary_storage import BinaryStorage
from supervisor.domain.ports.inventory import Inventory
from supervisor.domain.ports.metadata_storage import MetadataStorage
from supervisor.domain.ports.model_forward import ModelForward
from supervisor.domain.ports.station_config import StationConfig
from supervisor.domain.ports.telemetry_sink import TelemetrySink


class Config:
    ROOT_PATH = Path(__file__).parents[2]

    metadata_storage: MetadataStorage = None
    model_forward: ModelForward = None
    binary_storage: BinaryStorage = None
    inventory: Inventory = None
    station_config: StationConfig = None
    edge_station: EdgeStation = None
    telemetry_sink: TelemetrySink = None

    def get_metadata_storage(self):
        return self.metadata_storage

    def get_binary_storage(self):
        return self.binary_storage

    def get_model_forward(self):
        return self.model_forward

    def get_edge_station(self):
        return self.edge_station

    def get_inventory(self):
        return self.inventory

    def get_station_config(self):
        return self.station_config

    def get_telemetry_sink(self):
        return self.telemetry_sink
