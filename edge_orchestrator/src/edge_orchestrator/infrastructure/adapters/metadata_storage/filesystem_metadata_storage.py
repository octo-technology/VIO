import logging
from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class FileSystemMetadataStorage(IMetadataStorage):
    def __init__(self, metadata_storage_config: StorageConfig):
        self._storage_config: StorageConfig = metadata_storage_config
        self._logger = logging.getLogger(__name__)
        self.target_directory: Path = self._storage_config.target_directory
        self.target_directory.mkdir(parents=True, exist_ok=True)

    def save_item_metadata(self, item: Item):
        filepath = self._get_storing_path(item.id)
        with filepath.open("w") as f:
            f.write(item.model_dump_json(exclude={"binaries"}))
    
    def _get_storing_path(self, item_id: UUID) -> Path:
        path = self._storage_config.target_directory / f"{str(item_id)}.json"
        if self._storage_config.prefix:
            path = self._storage_config.target_directory / self._storage_config.prefix / f"{str(item_id)}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
