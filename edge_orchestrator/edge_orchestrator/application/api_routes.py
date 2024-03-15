from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from edge_orchestrator.api_config import (
    get_binary_storage,
    get_inventory,
    get_metadata_storage,
    get_station_config,
)
from edge_orchestrator.application.dto.station_config_dto import StationConfigDto
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.domain.ports.inventory import Inventory
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.domain.ports.station_config import StationConfig

api_router = APIRouter()


@api_router.get("/")
def home():
    return "the edge orchestrator is up and running"


@api_router.get("/items")
def read_all(metadata_storage: MetadataStorage = Depends(get_metadata_storage)):
    return metadata_storage.get_all_items_metadata()


@api_router.get("/items/{item_id}")
def get_item(
    item_id: str, metadata_storage: MetadataStorage = Depends(get_metadata_storage)
):
    return metadata_storage.get_item_metadata(item_id)


@api_router.get("/items/{item_id}/binaries/{camera_id}")
def get_item_binary(
    item_id: str,
    camera_id: str,
    binary_storage: BinaryStorage = Depends(get_binary_storage),
    station_config: StationConfig = Depends(get_station_config),
):
    content_binary = binary_storage.get_item_binary(
        item_id, camera_id, station_config.active_config_name
    )
    return Response(
        content=content_binary, status_code=HTTPStatus.OK, media_type="image/jpeg"
    )


@api_router.get("/items/{item_id}/binaries")
def get_item_binaries(
    item_id: str,
    binary_storage: BinaryStorage = Depends(get_binary_storage),
    station_config: StationConfig = Depends(get_station_config),
):
    return binary_storage.get_item_binaries(item_id, station_config.active_config_name)


@api_router.get("/items/{item_id}/state")
def get_item_state(
    item_id: str, metadata_storage: MetadataStorage = Depends(get_metadata_storage)
):
    return metadata_storage.get_item_state(item_id)


@api_router.get("/inventory")
def get_inventory(inventory: Inventory = Depends(get_inventory)):
    return inventory


@api_router.get("/configs")
def get_all_configs(station_config: StationConfig = Depends(get_station_config)):
    station_config.load()
    return station_config.all_configs


@api_router.get("/configs/active")
def get_active_config(station_config: StationConfig = Depends(get_station_config)):
    return station_config.active_config


@api_router.post("/configs/active")
def set_station_config(
    station_config_dto: StationConfigDto,
    station_config: StationConfig = Depends(get_station_config),
):
    if station_config_dto.config_name == "":
        return JSONResponse(
            status_code=403,
            content={"message": "No configuration selected!"},
        )
    station_config.set_station_config(station_config_dto.config_name)
    return station_config.active_config
