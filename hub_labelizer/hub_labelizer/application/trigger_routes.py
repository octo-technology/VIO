from fastapi import APIRouter, BackgroundTasks, Depends

from hub_labelizer.api_config import get_labelizer
from hub_labelizer.ports.labelizer import Labelizer

trigger_router = APIRouter()


@trigger_router.post("/labelize")
async def drop_to_labelizer_job(
    project_id: str = None,
    dataset_id: str = None,
    config_name: str = None,
    labelizer: Labelizer = Depends(get_labelizer),
    background_tasks: BackgroundTasks = None,
):
    filters = {}
    background_tasks.add_task(
        labelizer.apost_images, project_id, dataset_id, config_name, filters
    )
