from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)


class IMetadataStorageManager(ABC):
    _metadata_storage_factory: IMetadataStorageFactory
    _metadata_storages: dict[StorageType, IMetadataStorage]
    _logger: Logger

    @abstractmethod
    def get_metadata_storage(self, station_config: StationConfig) -> IMetadataStorage:
        pass

    @abstractmethod
    def reset(self, metadata_storage_factory: IMetadataStorageFactory):
        pass
