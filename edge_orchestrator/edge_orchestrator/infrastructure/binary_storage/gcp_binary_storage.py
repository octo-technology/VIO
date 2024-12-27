import os
from typing import List

from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


class GCPBinaryStorage(BinaryStorage):
    def __init__(self, prefix: str, active_config_name: str):
        self.storage_client = storage.Client()

        self.prefix = prefix
        self.active_config_name = active_config_name
        self.bucket = self.storage_client.get_bucket(os.getenv("GCP_BUCKET_NAME"))

    def save_item_binaries(self, item: Item) -> None:
        for camera_id, binary in item.binaries.items():
            blob = self.bucket.blob(os.path.join(self.prefix, self.active_config_name, item.id, f"{camera_id}.jpg"))
            if blob is None:
                raise Exception("An image should be upload")
            blob.upload_from_string(binary, content_type="image/jpg")

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filename = os.path.join(self.prefix, self.active_config_name, item_id, f"{camera_id}.jpg")
        blob = self.bucket.get_blob(filename)
        if blob is None:
            return None
        return blob.download_as_bytes()

    def get_item_binaries(self, item_id: str) -> List[str]:
        return [blob.name for blob in self.bucket.list_blobs() if item_id in blob.name]

    def get_item_binary_filepath(self, item_id: str, camera_id: str) -> str:
        return os.path.join(self.prefix, self.active_config_name, item_id, f"{camera_id}.jpg")
