from typing import List, Dict
import pymongo
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage


class MongoDbMetadataStorage(MetadataStorage):
    def __init__(self, mongodb_uri: str):
        self.client = pymongo.MongoClient(mongodb_uri)
        self.db = self.client['orchestratorDB']
        self.items_metadata = self.db['items']

    def save_item_metadata(self, item: Item):
        self.items_metadata.update_one({'_id': item.id}, {'$set': item.get_metadata()}, upsert=True)

    def get_item_metadata(self, item_id: str) -> Dict:
        return self.items_metadata.find_one({'_id': item_id})

    def get_item_state(self, item_id: str) -> str:
        item = self.items_metadata.find_one({'_id': item_id})
        return item["state"]

    def get_all_items_metadata(self) -> List[Dict]:
        return [item for item in self.items_metadata.find()]
