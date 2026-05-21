import logging
from typing import Dict, List
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import IBinaryStorage
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class AWSBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storing_path_manager: StoringPathManager = storing_path_manager
        self._bucket_name: str = station_config.binary_storage_config.bucket_name
        self._s3 = boto3.client("s3")

    def save_item_binaries(self, item: Item):
        self._logger.info(f"Saving item binaries for item {item.id}")
        for camera_id, image in item.binaries.items():
            if image.image_bytes is None:
                continue
            key = self._storing_path_manager.get_file_path(item.id, "jpg", camera_id).as_posix()
            self._s3.put_object(Bucket=self._bucket_name, Key=key, Body=image.image_bytes, ContentType="image/jpeg")
            self._logger.info(f"Image for camera {camera_id} uploaded to s3://{self._bucket_name}/{key}")
        self._logger.info(f"Item binaries saved for item {item.id}!")
        item.state = ItemState.SAVE_BINARIES

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        prefix = self._storing_path_manager.get_storing_path().as_posix()
        response = self._s3.list_objects_v2(Bucket=self._bucket_name, Prefix=prefix)
        return [obj["Key"].split("/")[-1] for obj in response.get("Contents", []) if str(item_id) in obj["Key"]]

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        prefix = self._storing_path_manager.get_storing_path().as_posix()
        response = self._s3.list_objects_v2(Bucket=self._bucket_name, Prefix=prefix)
        binaries: Dict[str, bytes] = {}
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if str(item_id) not in key:
                continue
            body = self._s3.get_object(Bucket=self._bucket_name, Key=key)["Body"].read()
            camera_id = key.rsplit("/", 1)[-1].rsplit("_", 1)[-1].split(".")[0]
            binaries[camera_id] = body
        return binaries

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        key = self._storing_path_manager.get_file_path(item_id, "jpg", camera_id).as_posix()
        try:
            return self._s3.get_object(Bucket=self._bucket_name, Key=key)["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                raise HTTPException(status_code=404, detail=f"The item {item_id} has no binary for {camera_id}")
            raise
