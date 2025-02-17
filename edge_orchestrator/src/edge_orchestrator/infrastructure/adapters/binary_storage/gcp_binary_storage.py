from http.client import HTTPException
import logging
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from google.cloud import storage


class GCPBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.get_bucket(station_config.binary_storage_config.target_directory.as_posix())

    def save_item_binaries(self, item: Item):
        for camera_id, image in item.binaries.items():
            blob = self._bucket.blob((self._get_storing_path(item.id) / f"{camera_id}.jpg").as_posix())
            if blob is None:
                raise Exception("An image should be upload")
            blob.upload_from_string(image.image_bytes, content_type="image/jpg")

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        binaries = []
        for blob in self._bucket.list_blobs(self._get_storing_path(item_id)):
            if item_id in blob.name:
                binaries.append(blob.name)
        return binaries

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        binaries = {}
        for blob in self._bucket.list_blobs(prefix=self._get_storing_path(item_id).as_posix()):
            if item_id in blob.name:
                binary = blob.download_as_bytes()
                camera_id = Path(blob.name).stem
                binaries[camera_id] = binary
        return binaries

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        filename = (self._get_storing_path(item_id) / f"{camera_id}.jpg").as_posix()
        blob = self._bucket.get_blob(filename)
        if blob is None:
            raise HTTPException(status_code=400, detail=f"The item {item_id} has no binary for {camera_id}")
        return blob.download_as_bytes()

    def _get_storing_directory_path(self) -> Path:
        return (
            Path(self._station_config.station_name) / self._station_config.binary_storage_config.prefix
            if self._station_config.binary_storage_config.prefix
            else Path(self._station_config.station_name)
        )

    def _get_storing_path(self, item_id: UUID) -> Path:
        return self._get_storing_directory_path() / str(item_id)
