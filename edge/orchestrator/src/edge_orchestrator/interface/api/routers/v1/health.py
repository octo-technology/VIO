import os

import aiohttp
from fastapi import APIRouter, Depends, HTTPException

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.interface.api.dependency_injection import get_config_manager

router = APIRouter(tags=["health"])


def _collect_urls(config_manager: ConfigManager) -> tuple[set[str], set[str]]:
    """Return (camera_urls, model_urls) from env vars + active config."""
    camera_urls: set[str] = set()
    model_urls: set[str] = set()
    if env_cam := os.getenv("CAMERA_SERVICE_URL"):
        camera_urls.add(env_cam.rstrip("/"))
    if env_model := os.getenv("SERVING_MODEL_URL"):
        model_urls.add(env_model.rstrip("/"))
    config = config_manager.get_config()
    if config:
        for cam in config.camera_configs.values():
            camera_urls.add(cam.service_url.rstrip("/"))
        for step in (config.pipeline_steps or {}).values():
            if step.model_forwarder_config and step.model_forwarder_config.model_serving_url:
                model_urls.add(str(step.model_forwarder_config.model_serving_url).rstrip("/"))
    return camera_urls, model_urls


async def _ping(url: str, path: str) -> dict[str, object]:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get(f"{url}{path}") as r:
                return {"ok": r.status == 200}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/health/live", summary="Liveness check")
def health_live():
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness check — active configuration required")
def health_ready(config_manager: ConfigManager = Depends(get_config_manager)):
    config = config_manager.get_config()
    if config is None:
        raise HTTPException(status_code=503, detail="No active configuration set")
    return {"status": "ready", "active_config": config.station_name}


@router.get("/health/services", summary="Health status of downstream services")
async def health_services(config_manager: ConfigManager = Depends(get_config_manager)):
    camera_urls, model_urls = _collect_urls(config_manager)
    results: dict[str, object] = {}
    for url in camera_urls:
        results[url] = {"service_type": "camera", **await _ping(url, "/health")}
    for url in model_urls:
        results[url] = {"service_type": "model_server", **await _ping(url, "/v1/capabilities")}
    return {"services": results}
