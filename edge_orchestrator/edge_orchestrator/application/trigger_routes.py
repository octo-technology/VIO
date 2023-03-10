from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.use_cases.uploader import Uploader

trigger_router = APIRouter()

supervisor = Supervisor()
uploader = Uploader()


@trigger_router.put('/trigger')
async def trigger_job(background_tasks: BackgroundTasks = None):
    item = Item.from_nothing()
    if supervisor.station_config.active_config is None:
        return JSONResponse(
            status_code=403,
            content={"message": "No active configuration selected! "
                                "Set the active station configuration before triggering the inspection."},
        )
    else:
        background_tasks.add_task(supervisor.inspect, item)
        return {'item_id': item.id}


@trigger_router.post('/trigger/image')
async def trigger_image_job(image: UploadFile = File(...), background_tasks:
                            BackgroundTasks = None):
    item = Item.from_nothing()
    if supervisor.station_config.active_config is None:
        return JSONResponse(
            status_code=403,
            content={"message": "No active configuration selected! "
                                "Set the active station configuration before triggering the inspection."},
        )
    else:
        contents = image.file.read()
        item.binaries = {'0': contents}
        background_tasks.add_task(supervisor.inspect, item)
        return {'item_id': item.id}


@trigger_router.post('/upload')
async def upload_job(image: UploadFile = File(...), background_tasks:
                     BackgroundTasks = None):
    item = Item.from_nothing()
    contents = image.file.read()
    item.binaries = {'0': contents}
    background_tasks.add_task(uploader.upload, item)
    return {'item_id': item.id}
