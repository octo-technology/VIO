from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.use_cases.supervisor import Supervisor

trigger_router = APIRouter()

supervisor = Supervisor()


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
