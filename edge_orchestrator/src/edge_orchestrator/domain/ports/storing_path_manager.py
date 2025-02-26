from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class StoringPathManager(metaclass=SingletonMeta):
    def __init__(self):
        self._storage_config = None
        self.station_name = None

    def get_storing_prefix_path(self) -> Path:
        return self._storage_config.target_directory / self.station_name

    def get_storing_path(self, item_id: UUID) -> Path:
        return self.get_storing_prefix_path() / str(item_id)

    def set(self, storage_config: StorageConfig, station_name: str):
        self._storage_config = storage_config
        self.station_name = station_name
