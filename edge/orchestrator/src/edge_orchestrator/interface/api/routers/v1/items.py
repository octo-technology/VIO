from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.interface.api.dependency_injection import (
    get_binary_storage_manager,
    get_config,
    get_metadata_storage_manager,
)

router = APIRouter(tags=["items"])


@router.get(
    "/items",
    summary="List all inspection items metadata",
    response_model_exclude_none=True,
)
def get_all_items_metadata(
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> List[Item]:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_all_items_metadata()


@router.get(
    "/items/{item_id}",
    summary="Get inspection item metadata",
    response_model_exclude_none=True,
)
def get_item_metadata(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> Item:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id)


@router.get(
    "/items/{item_id}/binaries",
    summary="List binary names stored for an item",
)
def get_item_binaries(
    item_id: UUID,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> List[str]:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return binary_storage.get_item_binary_names(item_id)


@router.get(
    "/items/{item_id}/binaries/{camera_id}",
    summary="Download a binary image for a given item and camera",
)
def get_item_binary(
    item_id: UUID,
    camera_id: str,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> Response:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return Response(content=binary_storage.get_item_binary(item_id, camera_id), media_type="image/jpeg")


@router.get(
    "/items/{item_id}/state",
    summary="Get the processing state of an item",
    response_model_exclude_none=True,
)
def get_item_state(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> ItemState:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id).state
