import json
import logging
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class FileSystemMetadataStorage(IMetadataStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self.target_directory: Path = self._station_config.metadata_storage_config.target_directory
        self.target_directory.mkdir(parents=True, exist_ok=True)
        self._storing_path_manager: StoringPathManager = storing_path_manager

    def save_item_metadata(self, item: Item):
        self._logger.info(f"Saving item metadata for item {item.id}")
        item.state = ItemState.DONE
        filepath = self._storing_path_manager.get_file_path(item.id, "json")

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w") as f:
            f.write(item.model_dump_json(exclude_none=True))
        self._logger.info(f"Item metadata for item {item.id} saved as {filepath.as_posix()}")

    def get_item_metadata(self, item_id: UUID) -> Item:
        filepath = self._storing_path_manager.get_file_path(item_id, "json")
        # TODO: test with non existing item metadata
        if not filepath.exists():
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no metadata")
        with filepath.open("r") as f:
            metadata = json.load(f)
        return Item(**metadata)

    def get_all_items_metadata(self):
        metadata = []
        for filepath in self._storing_path_manager.get_storing_prefix_path().glob("**/*.json"):
            try:
                with filepath.open("r") as f:
                    item_metadata = json.load(f)
                    metadata.append(Item(**item_metadata))
            except (ValueError, ValidationError):
                self._logger.exception(f"The following JSON file is invalid: {filepath.as_posix()}")
        return metadata
