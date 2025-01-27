from abc import abstractmethod
from logging import Logger
from pathlib import Path
from typing import Dict
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class IBinaryStorage:
    _storage_config: StorageConfig
    _logger: Logger

    @abstractmethod
    def save_item_binaries(self, item: Item):
        pass

    @abstractmethod
    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        pass

    # TODO: implement this method
    @abstractmethod
    def _get_storing_path(self, item_id: UUID) -> Path:
        pass
