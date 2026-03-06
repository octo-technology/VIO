from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.interface.api.dependency_injection import (
    get_config,
    get_config_manager,
)

router = APIRouter(tags=["configs"])


@router.get(
    "/configs",
    summary="List all available configurations",
    response_model_exclude_none=True,
)
def get_all_configs(
    reload: bool = False,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> Dict[str, StationConfig]:
    if reload:
        config_manager.reload_configs()
    configs = config_manager.all_configs
    if not configs:
        raise HTTPException(status_code=400, detail="No existing configuration")
    return configs


@router.get(
    "/configs/active",
    summary="Get the active configuration",
    response_model_exclude_none=True,
)
def get_active_config(station_config: StationConfig = Depends(get_config)) -> StationConfig:
    return station_config


@router.post(
    "/configs/active",
    summary="Set active configuration by name or full config body",
    response_model_exclude_none=True,
)
def set_config(
    request: Request,
    station_name: Optional[str] = None,
    station_config: Optional[StationConfig] = None,
    config_manager: ConfigManager = Depends(get_config_manager),
) -> StationConfig:
    if (station_name and station_config) or (station_name is None and station_config is None):
        raise HTTPException(status_code=422, detail="Either provide a station_name or a StationConfig (exclusive)")

    if station_name:
        config_manager.set_config_by_name(station_name)
    if station_config:
        config_manager.set_config(station_config)

    request.app.state.supervisor.reset_managers()
    request.app.state.data_gathering.reset_managers()

    return config_manager.get_config()
