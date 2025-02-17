from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class IMetadataStorageFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_metadata_storage(self, station_config: StationConfig) -> IMetadataStorage:
        pass
