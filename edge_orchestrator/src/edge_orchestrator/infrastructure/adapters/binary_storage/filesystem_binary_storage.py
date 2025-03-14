import logging
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException

from edge_orchestrator.domain.models.image_extension import ImageExtension
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class FileSystemBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storing_path_manager: StoringPathManager = storing_path_manager

    def save_item_binaries(self, item: Item):
        self._logger.info(f"Saving item binaries for item {item.id}")
        path = self._storing_path_manager.get_storing_path()
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, image in item.binaries.items():
            if image.image_bytes is None:
                continue
            filepath = self._storing_path_manager.get_file_path(item.id, "jpg", camera_id)
            item.binaries[camera_id].storing_path = filepath
            with filepath.open("wb") as f:
                f.write(image.image_bytes)
            self._logger.info(f"Image for camera {camera_id} saved as {filepath.as_posix()}")
        self._logger.info(f"Item binaries saved for item {item.id}!")
        item.state = ItemState.SAVE_BINARIES

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        path = self._storing_path_manager.get_storing_path()
        item_binaries = {}
        for extension in ImageExtension:
            for binary_path in path.glob(f"*.{extension.value}"):
                with binary_path.open("rb") as f:
                    item_binaries[binary_path.stem] = f.read()
        return item_binaries

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        path = self._storing_path_manager.get_storing_path()
        item_binaries = []
        for extension in ImageExtension:
            for binary_path in path.glob(f"*.{extension.value}"):
                item_binaries.append(binary_path.name)
        return item_binaries

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        filepath = self._storing_path_manager.get_file_path(item_id, "jpg", camera_id)
        # TODO: test with non existing item binary
        if not filepath.exists():
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no binary for {camera_id}")
        with filepath.open("rb") as f:
            return f.read()
