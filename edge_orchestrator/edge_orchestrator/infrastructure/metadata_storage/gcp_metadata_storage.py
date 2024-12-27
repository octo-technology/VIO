import json
import os
from typing import Dict, List

from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage


class GCPMetadataStorage(MetadataStorage):
    def __init__(self, prefix: str, active_config_name: str):
        self.storage_client = storage.Client()

        self.prefix = prefix
        self.active_config_name = active_config_name
        self.bucket = self.storage_client.get_bucket(os.getenv("GCP_BUCKET_NAME"))

    def save_item_metadata(self, item: Item):
        item_metadata = json.dumps(item.get_metadata())
        blob = self.bucket.blob(os.path.join(self.prefix, self.active_config_name, item.id, "metadata.json"))
        blob.upload_from_string(item_metadata, content_type="application/json")

    def get_item_metadata(self, item_id: str) -> Dict:
        filename = os.path.join(self.prefix, self.active_config_name, item_id, "metadata.json")
        blob = self.bucket.get_blob(filename)
        if blob is None:
            raise Exception("No file with this id exist")
        metadata = json.loads(blob.download_as_string())
        return metadata

    def get_item_state(self, item_id: str) -> str:
        item_metadata = self.get_item_metadata(item_id)
        return item_metadata["state"]

    def get_all_items_metadata(self) -> List[Dict]:
        metadatas = []
        for blob in self.bucket.list_blobs():
            if self.prefix in blob.name and "metadata.json" in blob.name:
                metadata = json.loads(blob.download_as_string())
                metadatas.append(metadata)
        return metadatas
