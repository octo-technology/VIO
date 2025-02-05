import logging

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)


class AzureBinaryStorage(IBinaryStorage):
    def __init__(self, storage_config: StorageConfig):
        self._storage_config: StorageConfig = storage_config
        self._logger = logging.getLogger(__name__)

    def save_item_binaries(self, item: Item):
        raise NotImplementedError("Not implemented yet")
