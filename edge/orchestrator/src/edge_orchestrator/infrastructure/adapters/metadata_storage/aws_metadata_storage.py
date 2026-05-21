import json
import logging
from typing import List
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import IMetadataStorage
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class AWSMetadataStorage(IMetadataStorage):
    def __init__(self, station_config: StationConfig, storing_path_manager: StoringPathManager):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)
        self._storing_path_manager: StoringPathManager = storing_path_manager
        self._bucket_name: str = station_config.metadata_storage_config.bucket_name
        self._s3 = boto3.client("s3")

    def save_item_metadata(self, item: Item):
        self._logger.info(f"Saving item metadata for item {item.id}")
        key = self._storing_path_manager.get_file_path(item.id, "json").as_posix()
        self._s3.put_object(
            Bucket=self._bucket_name,
            Key=key,
            Body=item.model_dump_json(exclude_none=True),
            ContentType="application/json",
        )
        self._logger.info(f"Item metadata for item {item.id} saved to s3://{self._bucket_name}/{key}")

    def get_item_metadata(self, item_id: UUID) -> Item:
        key = self._storing_path_manager.get_file_path(item_id, "json").as_posix()
        try:
            body = self._s3.get_object(Bucket=self._bucket_name, Key=key)["Body"].read()
            return Item(**json.loads(body))
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                raise HTTPException(status_code=404, detail=f"The item {item_id} has no metadata")
            raise

    def get_all_items_metadata(self) -> List[Item]:
        prefix = self._storing_path_manager.get_storing_prefix_path().as_posix()
        response = self._s3.list_objects_v2(Bucket=self._bucket_name, Prefix=prefix)
        items: List[Item] = []
        for obj in response.get("Contents", []):
            if not obj["Key"].endswith(".json"):
                continue
            try:
                body = self._s3.get_object(Bucket=self._bucket_name, Key=obj["Key"])["Body"].read()
                items.append(Item(**json.loads(body)))
            except Exception:
                self._logger.exception(f"Failed to load item metadata from s3://{self._bucket_name}/{obj['Key']}")
        return items
