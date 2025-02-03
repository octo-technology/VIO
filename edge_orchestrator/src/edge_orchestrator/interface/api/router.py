from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_manager import (
    ICameraRuleManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_manager import (
    IModelForwarderManager,
)
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_manager import (
    ItemRuleManager,
)
from edge_orchestrator.interface.api.dependency_injection import (
    get_binary_storage_manager,
    get_camera_manager,
    get_camera_rule_manager,
    get_item_rule_manager,
    get_metadata_storage_manager,
    get_model_forwarder_manager,
)
from edge_orchestrator.interface.api.models.item_in import ItemIn


async def get_health():
    return {"status": "ok"}


def set_config(station_config: StationConfig):
    manager = ConfigManager()
    manager.set_config(station_config)
    return {"message": f"Configuration updated successfully with {station_config.station_profile}"}


def get_config() -> StationConfig:
    manager = ConfigManager()
    config = manager.get_config()
    if not config:
        raise HTTPException(status_code=400, detail="No active configuration set")
    return config


def get_all_configs() -> Dict[str, StationConfig]:
    manager = ConfigManager()
    configs = manager.get_all_configs()
    if not configs:
        raise HTTPException(status_code=400, detail="No existing configuration")
    return configs


def get_supervisor(
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    model_forwarder_manager: IModelForwarderManager = Depends(get_model_forwarder_manager),
    camera_rule_manager: ICameraRuleManager = Depends(get_camera_rule_manager),
    item_rule_manager: ItemRuleManager = Depends(get_item_rule_manager),
    camera_manager: ICameraManager = Depends(get_camera_manager),
    station_config: StationConfig = Depends(get_config),
) -> Supervisor:
    supervisor = Supervisor(
        station_config,
        metadata_storage_manager,
        binary_storage_manager,
        model_forwarder_manager,
        camera_rule_manager,
        item_rule_manager,
        camera_manager,
    )
    supervisor._camera_manager.create_cameras(station_config)
    return supervisor


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
