from pathlib import Path
from typing import Optional
from uuid import UUID

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class StoringPathManager:
    def __init__(self, storage_config: StorageConfig, station_name: str):
        self._storage_config = storage_config
        self.station_name = station_name

    def get_storing_prefix_path(self) -> Path:
        return self._storage_config.target_directory / self.station_name

    def get_storing_path(self) -> Path:
        class_directory = self._storage_config.class_directory
        prefix_path = self.get_storing_prefix_path()
        return prefix_path / class_directory if class_directory else prefix_path

    def get_file_path(self, item_id: UUID, extension: str, camera_id: Optional[str] = None) -> Path:
        storing_path = self.get_storing_path()
        return (
            storing_path / f"{item_id}_{camera_id}.{extension}"
            if camera_id
            else storing_path / f"{item_id}.{extension}"
        )

    def set(self, storage_config: StorageConfig, station_name: str):
        self._storage_config = storage_config
