import json
import os
from typing import List, Optional

from dotenv import load_dotenv
from google.api_core.exceptions import NotFound
from google.cloud.storage import Client

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")

if BUCKET_NAME is None:
    raise ValueError("BUCKET_NAME environment variable is not set")

class GCPBinaryStorage:
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.bucket = Client().bucket(BUCKET_NAME)

    def get_edges_names(self) -> List[str]:
        iterator = self.bucket.list_blobs(prefix=self.prefix, delimiter="/")
        response = iterator._get_next_page_response()
        edges_names = [prefix.rstrip("/") for prefix in response["prefixes"]]
        return edges_names

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
        self, edge_name: str, use_case: str, prefix: Optional[str], item_id: str
    ) -> Optional[dict]:
        if prefix is None:
            metadata_blobname = f"{edge_name}/{use_case}/{item_id}.json"
        else:
            metadata_blobname = f"{edge_name}/{use_case}/{prefix}/{item_id}.json"

        return json.loads(self.get_text_blob(metadata_blobname))
