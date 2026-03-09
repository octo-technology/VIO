from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile

from edge_orchestrator.application.use_cases.data_gathering import DataGathering
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.image import Image
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.interface.api.dependency_injection import (
    get_config,
    get_data_gathering,
    get_supervisor,
)

router = APIRouter(tags=["jobs"])


@router.post("/trigger", summary="Trigger a visual inspection")
async def trigger_job(
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    supervisor: Supervisor = Depends(get_supervisor),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    input_binaries = {}
    for binary in binaries:
        input_binaries[binary.filename] = Image(image_bytes=await binary.read())
    item = Item(
        cameras_metadata=cameras_metadata,
        binaries=input_binaries,
    )
    background_tasks.add_task(supervisor.inspect, item, station_config)
    return {"item_id": item.id}


@router.post("/data_gathering", summary="Trigger a data gathering acquisition")
async def data_gathering_job(
    class_name: str = None,
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    data_gathering: DataGathering = Depends(get_data_gathering),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    station_config.binary_storage_config.class_directory = class_name
    station_config.metadata_storage_config.class_directory = class_name

    input_binaries = {}
    for binary in binaries:
        input_binaries[binary.filename] = Image(image_bytes=await binary.read())
    item = Item(
        cameras_metadata=cameras_metadata,
        binaries=input_binaries,
    )
    background_tasks.add_task(data_gathering.acquire, item, station_config)
    return {"item_id": item.id}


@router.post("/upload", summary="Upload binaries for data gathering")
async def upload_job(
    class_name: Optional[str] = None,
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    data_gathering: DataGathering = Depends(get_data_gathering),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    if class_name is None:
        class_name = "NA"
    station_config.binary_storage_config.class_directory = class_name
    station_config.metadata_storage_config.class_directory = class_name

    items = []
    for binary in binaries:
        item = Item(
            cameras_metadata=cameras_metadata,
            binaries={binary.filename: Image(image_bytes=await binary.read())},
        )
        items.append(item)
        background_tasks.add_task(data_gathering.upload, item, station_config)
    return {"items_ids": [item.id for item in items]}
