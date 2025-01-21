import logging
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class AzureMetadataStorage(IMetadataStorage):
    def __init__(self, storage_config: StorageConfig):
        self._storage_config: StorageConfig = storage_config
        self._logger = logging.getLogger(__name__)

    def save_item_metadata(self, item: Item):
        raise NotImplementedError("Not implemented yet")

    def get_storing_path(self, item_id: UUID):
        raise NotImplementedError("Not implemented yet")
