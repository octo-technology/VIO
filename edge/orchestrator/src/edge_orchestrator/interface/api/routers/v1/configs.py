import os
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.interface.api.dependency_injection import get_config_manager

router = APIRouter(tags=["configs"])


class ActivateConfigRequest(BaseModel):
    station_name: str


def _available_storage_types() -> list[str]:
    types = [StorageType.FILESYSTEM.value]
    if os.getenv("AWS_ACCESS_KEY_ID") or Path.home().joinpath(".aws", "credentials").exists():
        types.append(StorageType.AWS.value)
    if os.getenv("AZURE_STORAGE_CONNECTION_STRING") or os.getenv("AZURE_CLIENT_ID"):
        types.append(StorageType.AZURE.value)
    if (
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or Path.home().joinpath(".config", "gcloud", "application_default_credentials.json").exists()
    ):
        types.append(StorageType.GCP.value)
    return types


@router.get("/configs/options", summary="Available rule types and storage backends for config editing")
def get_config_options():
    return {
        "camera_rule_types": [e.value for e in CameraRuleType],
        "item_rule_types": [e.value for e in ItemRuleType],
        "storage_types": _available_storage_types(),
        "camera_types": [e.value for e in CameraType],
    }


@router.get("/configs/active", summary="Get the active configuration", response_model_exclude_none=True)
def get_active_config(config_manager: ConfigManager = Depends(get_config_manager)) -> StationConfig:
    config = config_manager.get_config()
    if config is None:
        raise HTTPException(status_code=404, detail="No active configuration")
    return config


@router.put("/configs/active", summary="Activate a configuration by name", response_model_exclude_none=True)
def activate_config(
    body: ActivateConfigRequest,
    request: Request,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> StationConfig:
    config_manager.set_config_by_name(body.station_name)
    request.app.state.supervisor.reset_managers()
    request.app.state.data_gathering.reset_managers()
    request.app.state.model_trainer_manager.reset()
    return config_manager.get_config()


@router.get("/configs", summary="List all available configurations", response_model_exclude_none=True)
def get_all_configs(config_manager: ConfigManager = Depends(get_config_manager)) -> Dict[str, StationConfig]:
    return config_manager.all_configs


@router.post("/configs", summary="Create a new configuration", status_code=201, response_model_exclude_none=True)
def create_config(
    station_config: StationConfig,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> StationConfig:
    if station_config.station_name in config_manager.all_configs:
        raise HTTPException(status_code=409, detail=f"Config '{station_config.station_name}' already exists")
    config_manager.save_config_only(station_config)
    return station_config


@router.get("/configs/{station_name}", summary="Get a configuration by name", response_model_exclude_none=True)
def get_config_by_name(
    station_name: str,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> StationConfig:
    config = config_manager.all_configs.get(station_name)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Config '{station_name}' not found")
    return config


@router.put("/configs/{station_name}", summary="Save a configuration", response_model_exclude_none=True)
def save_config(
    station_name: str,
    station_config: StationConfig,
    request: Request,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> StationConfig:
    station_config = station_config.model_copy(update={"station_name": station_name})
    config_manager.save_config_only(station_config)
    active = config_manager.get_config()
    if active and active.station_name == station_name:
        request.app.state.supervisor.reset_managers()
        request.app.state.data_gathering.reset_managers()
        request.app.state.model_trainer_manager.reset()
    return station_config


@router.delete("/configs/{station_name}", summary="Delete a configuration", status_code=204)
def delete_config(
    station_name: str,
    config_manager: ConfigManager = Depends(get_config_manager),
):
    config_manager.delete_config(station_name)
