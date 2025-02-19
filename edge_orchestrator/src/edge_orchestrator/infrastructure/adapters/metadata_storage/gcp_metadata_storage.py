import json
import logging
from http.client import HTTPException
from typing import List
from uuid import UUID

from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class GCPMetadataStorage(IMetadataStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.get_bucket(
            self._station_config.binary_storage_config.bucket_name.as_posix()
        )
        self._storing_path_manager: StoringPathManager = storing_path_manager

    def save_item_metadata(self, item: Item):
        item_metadata = item.model_dump_json(exclude_none=True)
        blob = self._bucket.blob(self._get_storing_path(item.id).as_posix())
        blob.upload_from_string(item_metadata, content_type="application/json")

    def get_item_metadata(self, item_id: UUID) -> Item:
        filename = (self._get_storing_path(item_id) / "metadata.json").as_posix()
        blob = self._bucket.get_blob(filename)
        if blob is None:
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no metadata")
        metadata = json.loads(blob.download_as_string())
        return Item(**metadata)

    def get_all_items_metadata(self) -> List[Item]:
        metadatas = []
        for blob in self._bucket.list_blobs(prefix=self._storing_path_manager.get_storing_prefix_path()):
            if blob.name.endswith(".json"):
                metadata = json.loads(blob.download_as_string())
                metadatas.append(Item(**metadata))
        return metadatas
