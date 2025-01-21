from fastapi import APIRouter, BackgroundTasks, Depends

from edge_orchestrator.application.dependencies.config_dependency import (
    get_all_configs,
    get_config,
    get_supervisor,
)
from edge_orchestrator.application.models.item_in import ItemIn
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.services.config_manager import ConfigManager
from edge_orchestrator.domain.use_cases.supervisor import Supervisor


async def get_health():
    return {"status": "ok"}


def set_config(station_config: StationConfig):
    manager = ConfigManager()
    manager.set_config(station_config)
    return {"message": f"Configuration updated successfully with {station_config.station_profile}"}


async def trigger_job(
    item_in: ItemIn, supervisor: Supervisor = Depends(get_supervisor), background_tasks: BackgroundTasks = None
):
    background_tasks.add_task(supervisor.inspect, item_in)
    return {"item_id": item_in.id}


router = APIRouter(prefix="/api/v1")
router.add_api_route("/health/live", get_health, methods=["GET"])
router.add_api_route("/set_config", set_config, methods=["POST"])
router.add_api_route("/get_config", get_config, methods=["GET"])
router.add_api_route("/get_all_configs", get_all_configs, methods=["GET"])
router.add_api_route("/trigger_job", trigger_job, methods=["POST"])
