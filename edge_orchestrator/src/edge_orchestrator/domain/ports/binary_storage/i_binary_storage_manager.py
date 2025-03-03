from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)


class IBinaryStorageManager(ABC):
    _binary_storage_factory: IBinaryStorageFactory
    _binary_storages: dict[StorageType, IBinaryStorage]
    _logger: Logger

    @abstractmethod
    def get_binary_storage(self, station_config: StationConfig) -> IBinaryStorage:
        pass

    @abstractmethod
    def reset(self, binary_storage_factory: IBinaryStorageFactory):
        pass
