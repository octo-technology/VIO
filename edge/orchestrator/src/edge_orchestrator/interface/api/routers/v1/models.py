import aiohttp
from fastapi import APIRouter, Depends, HTTPException

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.interface.api.dependency_injection import get_config_manager
from edge_orchestrator.interface.api.routers.v1.health import _collect_urls

router = APIRouter(tags=["models"])


@router.get("/models/available", summary="Available model names per model server URL")
async def get_models_available(config_manager: ConfigManager = Depends(get_config_manager)):
    _, model_urls = _collect_urls(config_manager)
    result: dict[str, list[str]] = {}
    for url in model_urls:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(f"{url.rstrip('/')}/v1/capabilities") as r:
                    if r.status == 200:
                        body = await r.json(content_type=None)
                        result[url] = list((body.get("models") or {}).keys())
                    else:
                        result[url] = []
        except Exception:
            result[url] = []
    return {"models": result}


@router.get("/models/metadata", summary="Proxy model metadata from model server")
async def get_model_metadata(serving_url: str, model_name: str):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
            async with session.get(f"{serving_url.rstrip('/')}/v1/models/{model_name}/metadata") as r:
                if r.status == 200:
                    return await r.json(content_type=None)
                raise HTTPException(status_code=r.status, detail=f"Model server returned {r.status}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
