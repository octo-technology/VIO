import aiohttp
from fastapi import APIRouter, Depends

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.interface.api.dependency_injection import get_config_manager
from edge_orchestrator.interface.api.routers.v1.health import _collect_urls

router = APIRouter(tags=["cameras"])


@router.get("/cameras/available", summary="Available cameras per service URL with their backend type")
async def get_cameras_available(config_manager: ConfigManager = Depends(get_config_manager)):
    camera_urls, _ = _collect_urls(config_manager)
    result: dict[str, dict[str, dict]] = {}
    for url in camera_urls:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(f"{url}/capabilities") as r:
                    if r.status == 200:
                        body = await r.json(content_type=None)
                        result[url] = {
                            cam_id: {
                                "backend": cam_info.get("backend", "unknown"),
                                "position": cam_info.get("position"),
                            }
                            for cam_id, cam_info in (body.get("cameras") or {}).items()
                        }
                    else:
                        result[url] = {}
        except Exception:
            result[url] = {}
    return {"cameras": result}
