from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from edge_orchestrator.api_config import get_station_config

from edge_orchestrator.domain.ports.station_config import StationConfig
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
    background_tasks: BackgroundTasks = None
):
    item = Item.from_nothing()
    contents = image.file.read()
    item.binaries = {"0": contents}
    background_tasks.add_task(uploader.upload, item, station_config.active_config_name)
    return {"item_id": item.id}
