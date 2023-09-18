import os
import secrets
from typing import List, Optional

from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


class GCPBucketBinaryStorage(BinaryStorage):
    def __init__(self, prefix: Optional[str] = None, bucket_name: Optional[str] = None):
        if prefix is None:
            prefix = os.environ.get("EDGE_NAME", f"edge#{secrets.token_hex(4)}")
        if bucket_name is None:
            bucket_name = os.getenv("GCP_BUCKET_NAME")

        self.prefix = prefix
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(bucket_name)

    def save_item_binaries(self, item: Item) -> None:
        for camera_id, binary in item.binaries.items():
            blob = self.bucket.blob(
                os.path.join(self.prefix, item.id, f"{camera_id}.jpg")
            )
            if blob is None:
                raise Exception("An image should be upload")
            blob.upload_from_string(binary, content_type="image/jpg")

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filename = os.path.join(self.prefix, item_id, f"{camera_id}.jpg")
        blob = self.bucket.get_blob(filename)
        if blob is None:
            return None
        return blob.download_as_bytes()

    def get_item_binaries(self, item_id: str) -> List[str]:
        binaries = []
        for blob in self.bucket.list_blobs():
            if item_id in blob.name:
                for binary in self.bucket.list_blobs(prefix=blob.name):
                    binary = binary.name
                    binaries.append(binary)
        return binaries
