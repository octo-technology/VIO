import logging
from http.client import HTTPException
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from google.cloud import storage

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class GCPBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.get_bucket(station_config.binary_storage_config.bucket_name)
        self._storing_path_manager: StoringPathManager = storing_path_manager

    def save_item_binaries(self, item: Item):
        self._logger.info(f"Saving item binaries for item {item.id}")
        for camera_id, image in item.binaries.items():
            blob = self._bucket.blob(self._storing_path_manager.get_file_path(item.id, "jpg", camera_id).as_posix())
            if blob is None:
                raise Exception("An image should be upload")
            blob.upload_from_string(image.image_bytes, content_type="image/jpg")
            self._logger.info(f"Image for camera {camera_id} saved as {blob.name}")
        self._logger.info(f"Item binaries saved for item {item.id}!")
        item.state = ItemState.SAVE_BINARIES

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        binaries = []
        for blob in self._bucket.list_blobs(self._storing_path_manager.get_storing_path()):
            if item_id in blob.name:
                binaries.append(blob.name)
        return binaries

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        binaries = {}
        for blob in self._bucket.list_blobs(prefix=self._storing_path_manager.get_storing_path().as_posix()):
            if item_id in blob.name:
                binary = blob.download_as_bytes()
                camera_id = Path(blob.name).stem
                binaries[camera_id] = binary
        return binaries

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        filename = (self._storing_path_manager.get_file_path(item_id, "jpg", camera_id)).as_posix()
        blob = self._bucket.get_blob(filename)
        if blob is None:
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no binary for {camera_id}")
        return blob.download_as_bytes()
