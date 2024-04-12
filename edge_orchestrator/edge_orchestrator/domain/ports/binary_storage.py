from abc import abstractmethod
from typing import List

from edge_orchestrator.domain.models.item import Item


class BinaryStorage:
    @abstractmethod
    def save_item_binaries(self, item: Item, active_config_name: str):
        pass

    @abstractmethod
    def get_item_binary(self, item_id: str, camera_id: str, active_config_name: str) -> bytes:
        pass

    @abstractmethod
    def get_item_binaries(self, item_id: str, active_config_name: str) -> List[str]:
        pass
