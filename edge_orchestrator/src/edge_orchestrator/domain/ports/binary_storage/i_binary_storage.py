from abc import abstractmethod
from logging import Logger
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig


class IBinaryStorage:
    _station_config: StationConfig
    _logger: Logger

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

    # TODO: implement this method
    @abstractmethod
    def _get_storing_path(self, item_id: UUID) -> Path:
        pass
