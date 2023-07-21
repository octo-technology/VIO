from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from typing_extensions import Annotated

from application.dto.station_config import StationConfig
from edge_orchestrator.api_config import (
    get_supervisor,
    get_station_config,
    get_uploader,
)
from edge_orchestrator.domain.models.item import Item

trigger_router = APIRouter()


@trigger_router.post("/trigger")
async def trigger_job(
    station_config: Annotated[StationConfig, Depends(get_station_config)],
    image: UploadFile = None,
    background_tasks: BackgroundTasks = None,
):
    if station_config.active_config:
        supervisor = get_supervisor()
        item = Item.from_nothing()
        if image:
            contents = image.file.read()
            camera_id = supervisor.station_config.get_cameras()[0]
            item.binaries = {camera_id: contents}
        background_tasks.add_task(supervisor.inspect, item)
        return {"item_id": item.id}
    else:
        return JSONResponse(
            status_code=403,
            content={
                "message": "No active configuration selected! "
                "Set the active station configuration before triggering the inspection."
            },
        )


@trigger_router.post("/upload")
async def upload_job(
    station_config: Annotated[StationConfig, Depends(get_station_config)],
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    if station_config.active_config:
        uploader = get_uploader()
        item = Item.from_nothing()
        contents = image.file.read()
        item.binaries = {"0": contents}
        background_tasks.add_task(uploader.upload, item)
        return {"item_id": item.id}
    else:
        return JSONResponse(
            status_code=403,
            content={
                "message": "No active configuration selected! "
                "Set the active station configuration before uploading the image."
            },
        )
