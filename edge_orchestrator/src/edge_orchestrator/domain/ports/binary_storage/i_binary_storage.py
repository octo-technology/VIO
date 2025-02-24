from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict, List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class IBinaryStorage(ABC):
    _station_config: StationConfig
    _logger: Logger
    _storing_path_manager: StoringPathManager

    @abstractmethod
    def save_item_binaries(self, item: Item):
        pass

    @abstractmethod
    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        pass

    @abstractmethod
    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        pass

    @abstractmethod
    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        pass
