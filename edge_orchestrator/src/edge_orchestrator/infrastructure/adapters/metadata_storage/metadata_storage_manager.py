import logging

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)


class MetadataStorageManager(IMetadataStorageManager):
    def __init__(self, metadata_storage_factory: IMetadataStorageFactory):
        self._metadata_storage_factory = metadata_storage_factory
        self._metadata_storages = {}
        self._logger = logging.getLogger(__name__)

    def get_metadata_storage(self, storage_config: StorageConfig) -> IMetadataStorage:
        metadata_storage_type = storage_config.storage_type
        if metadata_storage_type not in self._metadata_storages:
            metadata_storage = self._metadata_storage_factory.create_metadata_storage(storage_config)
            self._metadata_storages[metadata_storage_type] = metadata_storage
        return self._metadata_storages[metadata_storage_type]
