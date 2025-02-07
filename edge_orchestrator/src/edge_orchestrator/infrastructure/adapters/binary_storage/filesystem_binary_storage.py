import logging
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)


class FileSystemBinaryStorage(IBinaryStorage):
    def __init__(self, binary_storage_config: StorageConfig):
        self._storage_config: StorageConfig = binary_storage_config
        self._logger = logging.getLogger(__name__)

    def save_item_binaries(self, item: Item):
        path = self._get_storing_path(item.id)
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, image in item.binaries.items():
            filepath = path / f"{camera_id}.jpg"
            item.binaries[camera_id].storing_path = filepath
            with filepath.open("wb") as f:
                f.write(image.image_bytes)

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        path = self._get_storing_path(item_id)
        item_binaries = {}
        for binary_path in path.glob("*"):
            with binary_path.open("rb") as f:
                item_binaries[binary_path.stem] = f.read()
        return item_binaries

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        path = self._get_storing_path(item_id)
        item_binaries = []
        for binary_path in path.glob("*"):
            item_binaries.append(binary_path.name)
        return item_binaries

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        filepath = self._get_storing_path(item_id) / f"{camera_id}.jpg"
        with filepath.open("rb") as f:
            return f.read()

    def _get_storing_directory_path(self) -> Path:
        return (
            self._storage_config.target_directory / self._storage_config.prefix
            if self._storage_config.prefix
            else self._storage_config.target_directory
        )

    def _get_storing_path(self, item_id: UUID) -> Path:
        return self._get_storing_directory_path() / str(item_id)
