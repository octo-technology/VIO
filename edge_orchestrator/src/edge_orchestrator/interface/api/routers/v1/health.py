from fastapi import APIRouter, Depends, HTTPException

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.interface.api.dependency_injection import get_config_manager

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness check")
def health_live():
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness check — active configuration required")
def health_ready(config_manager: ConfigManager = Depends(get_config_manager)):
    config = config_manager.get_config()
    if config is None:
        raise HTTPException(status_code=503, detail="No active configuration set")
    return {"status": "ready", "active_config": config.station_name}
