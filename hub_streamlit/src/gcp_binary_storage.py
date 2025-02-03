import json
import os
from typing import Optional

from dotenv import load_dotenv
from google.api_core.exceptions import NotFound
from google.cloud.storage import Client

load_dotenv()

BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")


class GCPBinaryStorage:
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.bucket = Client().bucket(BUCKET_NAME)

    def get_text_blob(self, blobname: str) -> str:
        blob = self.bucket.blob(blobname)
        try:
            text_blob = blob.download_as_text()
        except NotFound as e:
            print(f"Blob not found for {blobname}")
            print(f"Error: {e}")
            text_blob = None
        return text_blob

    def extract_metadata(
        self, edge_name: str, use_case: str, item_id: str
    ) -> Optional[dict]:
        metadata_blobname = f"{edge_name}/{use_case}/{item_id}/metadata.json"

        return json.loads(self.get_text_blob(metadata_blobname))
