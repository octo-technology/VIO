import os
from typing import List
from datetime import datetime

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from google.cloud import storage


class GCPBinaryStorage(BinaryStorage):
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(os.getenv('GCP_BUCKET_NAME'))
        self.dt_string = datetime.now().strftime("%d-%m-%Y")

    def save_item_binaries(self, item: Item) -> None:
        for camera_id, binary in item.binaries.items():
            blob = self.bucket.blob(
                f"{self.dt_string}_{item.id}/{camera_id}.jpg"
            )
            blob.upload_from_string(binary, content_type="image/jpg")

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filename = f"{item_id}/{camera_id}.jpg"
        binary = None
        for blob in self.bucket.list_blobs():
            if filename in blob.name:
                binary = blob.download_as_bytes()
        return binary

    def get_item_binaries(self, item_id: str) -> List[str]:
        binaries = []
        for blob in self.bucket.list_blobs():
            if item_id in blob.name:
                for binary in self.bucket.list_blobs(prefix=blob.name):
                    binary = binary.name
                    binaries.append(binary)
        return binaries
