import logging
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)


class FileSystemBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)

    def save_item_binaries(self, item: Item):
        path = self._get_storing_path(item.id)
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, image in item.binaries.items():
            if image.image_bytes is None:
                continue
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
        # TODO: test with non existing item binary
        if not filepath.exists():
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no binary for {camera_id}")
        with filepath.open("rb") as f:
            return f.read()

    def _get_storing_directory_path(self) -> Path:
        return (
            self._station_config.binary_storage_config.target_directory
            / self._station_config.station_name
            / self._station_config.binary_storage_config.prefix
            if self._station_config.binary_storage_config.prefix
            else self._station_config.binary_storage_config.target_directory / self._station_config.station_name
        )

    def _get_storing_path(self, item_id: UUID) -> Path:
        return self._get_storing_directory_path() / str(item_id)
