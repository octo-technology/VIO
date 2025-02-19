import json
import logging
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class FileSystemMetadataStorage(IMetadataStorage):
    def __init__(self, station_config: StationConfig):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self.target_directory: Path = self._station_config.metadata_storage_config.target_directory
        self.target_directory.mkdir(parents=True, exist_ok=True)

    def save_item_metadata(self, item: Item):
        filepath = self._get_storing_path(item.id)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w") as f:
            f.write(item.model_dump_json(exclude_none=True))

    def get_item_metadata(self, item_id: UUID) -> Item:
        filepath = (self._get_storing_path(item_id) / "metadata.json").as_posix()
        # TODO: test with non existing item metadata
        if not filepath.exists():
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no metadata")
        with filepath.open("r") as f:
            metadata = json.load(f)
        return Item(**metadata)

    def get_all_items_metadata(self):
        metadata = []
        for filepath in self._get_storing_directory_path().glob("**/*.json"):
            try:
                with filepath.open("r") as f:
                    item_metadata = json.load(f)
                    metadata.append(Item(**item_metadata))
            except (ValueError, ValidationError):
                self._logger.exception(f"The following JSON file is invalid: {filepath.as_posix()}")
        return metadata

    def _get_storing_directory_path(self) -> Path:
        return (
            self._station_config.metadata_storage_config.target_directory
            / self._station_config.station_name
            / self._station_config.metadata_storage_config.prefix
            if self._station_config.metadata_storage_config.prefix
            else self._station_config.metadata_storage_config.target_directory / self._station_config.station_name
        )

    def _get_storing_path(self, item_id: UUID) -> Path:
        return self._get_storing_directory_path() / str(item_id)
