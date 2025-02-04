from abc import abstractmethod
from logging import Logger
from pathlib import Path
from typing import List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class IMetadataStorage:
    _storage_config: StorageConfig
    _logger: Logger

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
