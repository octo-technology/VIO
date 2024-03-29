from abc import abstractmethod
from typing import Dict, List

from edge_orchestrator.domain.models.item import Item


class MetadataStorage:
    @abstractmethod
    def save_item_metadata(self, item: Item, active_config_name: str):
        pass

    @abstractmethod
    def get_item_metadata(self, item_id: str, active_config_name: str) -> Dict:
        pass

    @abstractmethod
    def get_item_state(self, item_id: str, active_config_name: str) -> str:
        pass

    @abstractmethod
    def get_all_items_metadata(self) -> List[Dict]:
        pass
