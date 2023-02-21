import json
from typing import Dict, List
from datetime import datetime
from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage


BUCKET_NAME = "augi_vio_storage"


class GCPMetadataStorage(MetadataStorage):
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(BUCKET_NAME)
        self.dt_string = datetime.now().strftime("%d-%m-%Y")

    def save_item_metadata(self, item: Item):
        item_metadata = json.dumps(item.get_metadata())
        blob = self.bucket.blob(f"{self.dt_string}_{item.id}/metadata.json")
        blob.upload_from_string(item_metadata, content_type="application/json")

    def get_item_metadata(self, item_id: str) -> Dict:
        filename = f"{self.dt_string}_{item_id}/metadata.json"
        blob = self.bucket.get_blob(filename)
        metadata = json.loads(blob.download_as_string())
        return metadata

    def get_item_state(self, item_id: str) -> str:
        item_metadata = self.get_item_metadata(item_id)
        return item_metadata["state"]

    def get_all_items_metadata(self) -> List[Dict]:

        metadatas = []
        for blob in self.bucket.list_blobs():
            if "metadata.json" in blob.name:
                metadata = json.loads(blob.download_as_string())
                metadatas.append(metadata)
        return metadatas
