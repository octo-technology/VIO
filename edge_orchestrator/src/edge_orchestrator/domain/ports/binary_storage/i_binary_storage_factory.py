from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)


class IBinaryStorageFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_binary_storage(self, station_config: StationConfig) -> IBinaryStorage:
        pass
