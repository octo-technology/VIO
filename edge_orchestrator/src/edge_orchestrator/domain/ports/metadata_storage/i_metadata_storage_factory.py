from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class IMetadataStorageFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_metadata_storage(self, storage_config: StorageConfig) -> IMetadataStorage:
        pass
