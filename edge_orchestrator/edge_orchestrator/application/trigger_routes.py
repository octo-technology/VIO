from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from edge_orchestrator.api_config import get_station_config, get_labelizer, get_binary_storage, get_metadata_storage

from edge_orchestrator.domain.ports.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.domain.ports.labelizer import Labelizer
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.use_cases.uploader import Uploader

trigger_router = APIRouter()

supervisor = Supervisor()
uploader = Uploader()


@trigger_router.post("/trigger")
async def trigger_job(
    image: UploadFile = None, background_tasks: BackgroundTasks = None
):
    item = Item.from_nothing()
    if supervisor.station_config.active_config is None:
        return JSONResponse(
            status_code=403,
            content={
                "message": "No active configuration selected! "
                "Set the active station configuration before triggering the inspection."
            },
        )
    else:
        if image:
            contents = image.file.read()
            camera_id = supervisor.station_config.get_cameras()[0]
            item.binaries = {camera_id: contents}
        background_tasks.add_task(supervisor.inspect, item)
        return {"item_id": item.id}


@trigger_router.post("/upload")
async def upload_job(
    image: UploadFile = File(...),
    station_config: StationConfig = Depends(get_station_config),
    background_tasks: BackgroundTasks = None,
):
    item = Item.from_nothing()
    contents = image.file.read()
    item.binaries = {"0": contents}
    background_tasks.add_task(
        uploader.upload, item, station_config.active_config["name"]
    )
    return {"item_id": item.id}


@trigger_router.post("/drop_to_labelizer")
async def drop_to_labelizer_job(
        dataset_id: str = None,
        dataset_name: str = None,
        station_config: StationConfig = Depends(get_station_config),
        metadata_storage: MetadataStorage = Depends(get_metadata_storage),
        binary_storage: BinaryStorage = Depends(get_binary_storage),
        labelizer: Labelizer = Depends(get_metadata_storage),
        background_tasks: BackgroundTasks = None,
):
    active_config_folder_name = station_config.active_config["name"]
    filters = {}
    background_tasks.add_task(
        labelizer.post_images(),
        dataset_id,
        dataset_name,
        active_config_folder_name,
        metadata_storage,
        binary_storage,
        filters
    )
