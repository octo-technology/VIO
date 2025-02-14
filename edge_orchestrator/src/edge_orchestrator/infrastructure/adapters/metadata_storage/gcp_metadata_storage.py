from http.client import HTTPException
import json
import logging
from pathlib import Path
from typing import List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from google.cloud import storage


class GCPMetadataStorage(IMetadataStorage):
    def __init__(self, metadata_storage_config: StorageConfig):
        self._storage_config: StorageConfig = metadata_storage_config
        self._logger = logging.getLogger(__name__)
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.get_bucket(self._storage_config.target_directory.as_posix())

    def save_item_metadata(self, item: Item):
        item_metadata = item.model_dump_json(exclude_none=True)
        blob = self._bucket.blob(self._get_storing_path(item.id).as_posix())
        blob.upload_from_string(item_metadata, content_type="application/json")

    def get_item_metadata(self, item_id: UUID) -> Item:
        filename = self._get_storing_path(item_id).as_posix()
        blob = self._bucket.get_blob(filename)
        if blob is None:
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no metadata")
        metadata = json.loads(blob.download_as_string())
        return Item(**metadata)

    def get_all_items_metadata(self) -> List[Item]:
        metadatas = []
        for blob in self._bucket.list_blobs(prefix=self._get_storing_directory_path()):
            if blob.name.endswith(".json"):
                metadata = json.loads(blob.download_as_string())
                metadatas.append(Item(**metadata))
        return metadatas

    def _get_storing_directory_path(self) -> Path:
        return (
            self._storage_config.target_directory / self._storage_config.prefix
            if self._storage_config.prefix
            else self._storage_config.target_directory
        )

    def _get_storing_path(self, item_id: UUID) -> Path:
        return self._get_storing_directory_path() / f"{str(item_id)}.json"
