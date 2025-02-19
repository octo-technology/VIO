from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class IMetadataStorage(ABC):
    _station_config: StationConfig
    _logger: Logger
    _storing_path_manager: StoringPathManager

    @abstractmethod
    def save_item_metadata(self, item: Item):
        pass

    @abstractmethod
    def get_item_metadata(self, item_id: UUID) -> Item:
        pass

    @abstractmethod
    def get_all_items_metadata(self) -> List[Item]:
        pass

    # TODO: see how it can be merged with same method in IBinaryStorage
    @abstractmethod
    def _get_storing_path(self, item_id: UUID) -> Path:
        pass
