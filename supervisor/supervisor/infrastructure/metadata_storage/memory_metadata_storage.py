from typing import Dict, List

from supervisor.domain.models.item import Item
from supervisor.domain.ports.metadata_storage import MetadataStorage


class MemoryMetadataStorage(MetadataStorage):
    def __init__(self):
        self.items_metadata = {}

    def save_item_metadata(self, item: Item):
        if item.id in self.items_metadata:
            self.items_metadata[item.id].update(item.get_metadata())
        else:
            self.items_metadata[item.id] = item.get_metadata()

    def get_item_metadata(self, item_id: str) -> Dict:
        return self.items_metadata[item_id]

    def get_item_state(self, item_id: str) -> str:
        item = self.items_metadata[item_id]
        return item["state"]

    def get_all_items_metadata(self) -> List[Dict]:
        return [item for item in self.items_metadata.values()]
