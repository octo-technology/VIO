from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import Response
from typing_extensions import Annotated

from edge_orchestrator import logger
from edge_orchestrator.api_config import (
    get_metadata_storage,
    get_station_config,
    get_binary_storage,
)
from edge_orchestrator.application.config import (
    Settings,
    get_settings,
)
from edge_orchestrator.application.dto.station_config import StationConfig
from edge_orchestrator.application.dto.station_config_dto import StationConfigDto
from edge_orchestrator.application.no_active_configuration_exception import (
    NoActiveConfigurationException,
)
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage

api_router = APIRouter()


@api_router.get("/")
async def home(settings: Annotated[Settings, Depends(get_settings)]):
    infos = {"status": "edge-orchestrator up and running"}
    infos.update(settings.model_dump(mode="json"))
    return infos


@api_router.get("/items")
def read_all(
        metadata_storage: Annotated[MetadataStorage, Depends(get_metadata_storage)]
):
    return metadata_storage.get_all_items_metadata()


@api_router.get("/items/{item_id}")
def get_item(
        item_id: str,
        metadata_storage: Annotated[MetadataStorage, Depends(get_metadata_storage)],
):
    return metadata_storage.get_item_metadata(item_id)


@api_router.get("/items/{item_id}/binaries/{camera_id}")
def get_item_binary(
        item_id: str,
        camera_id: str,
        binary_storage: BinaryStorage = Depends(get_binary_storage),
):
    content_binary = binary_storage.get_item_binary(item_id, camera_id)
    return Response(
        content=content_binary, status_code=HTTPStatus.OK, media_type="image/jpeg"
    )


#
@api_router.get("/items/{item_id}/binaries")
def get_item_binaries(
        item_id: str,
        binary_storage: BinaryStorage = Depends(get_binary_storage),
):
    return binary_storage.get_item_binaries(item_id)


@api_router.get("/items/{item_id}/state")
def get_item_state(
        item_id: str,
        metadata_storage: MetadataStorage = Depends(get_metadata_storage),
):
    return metadata_storage.get_item_state(item_id)


@api_router.get("/configs")
def get_all_configs(station_config: StationConfig = Depends(get_station_config)) -> List[StationConfig]:
    station_config.load()
    return station_config.all_configs


@api_router.get("/configs/active")
def get_active_config(station_config: StationConfig = Depends(get_station_config)):
    if station_config.active_config is None:
        raise NoActiveConfigurationException("no_active_configuration")
    return station_config.active_config


@api_router.post("/configs/active")
def set_active_config(
        station_config_dto: StationConfigDto,
        station_config: StationConfig = Depends(get_station_config),
):
    station_config.set_station_config(station_config_dto.config_name)
    return station_config.active_config


@api_router.post("/config")
def set_config(
        station_config_dto: StationConfig,
):
    logger.info(f"set config {station_config_dto.to_model()} to")
