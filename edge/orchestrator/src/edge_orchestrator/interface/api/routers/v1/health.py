import aiohttp
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


@router.get("/health/services", summary="Downstream service health (camera, model server)")
async def health_services(config_manager: ConfigManager = Depends(get_config_manager)):
    config = config_manager.get_config()

    camera_urls: set[str] = set()
    model_urls: set[str] = set()

    if config:
        for cam in config.camera_configs.values():
            camera_urls.add(cam.service_url.rstrip("/"))
        for step in (config.pipeline_steps or {}).values():
            if step.model_forwarder_config and step.model_forwarder_config.model_serving_url:
                model_urls.add(str(step.model_forwarder_config.model_serving_url).rstrip("/"))

    async def probe(url: str, path: str) -> bool:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(f"{url}{path}") as r:
                    return r.status < 500
        except Exception:
            return False

    results: dict = {}
    for url in camera_urls:
        results[url] = await probe(url, "/health")
    for url in model_urls:
        results[url] = await probe(url, "/v1/")

    return {"services": results}
