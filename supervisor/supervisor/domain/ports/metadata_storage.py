from abc import abstractmethod
from typing import List, Dict

from supervisor.domain.models.item import Item


class MetadataStorage:

    @abstractmethod
    def save_item_metadata(self, item: Item):
        pass

    @abstractmethod
    def get_item_metadata(self, item_id: str) -> Dict:
        pass

    @abstractmethod
    def get_item_state(self, item_id: str) -> str:
        pass

    @abstractmethod
    def get_all_items_metadata(self) -> List[Dict]:
        pass
