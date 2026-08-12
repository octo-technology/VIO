from typing import List

import aiohttp
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.domain.exceptions import ModelNotInConfigError
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer_manager import (
    IModelTrainerManager,
)
from edge_orchestrator.interface.api.dependency_injection import (
    get_config,
    get_config_manager,
    get_model_trainer_manager,
)
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


@router.post(
    "/models/{model_name}/reference-images",
    summary="Teach a model new anomaly-free reference images",
    status_code=202,
)
async def add_reference_images(
    model_name: str,
    files: List[UploadFile] = File(default=[]),
    manager: IModelTrainerManager = Depends(get_model_trainer_manager),
    station_config: StationConfig = Depends(get_config),
) -> TrainingJob:
    if not files:
        raise HTTPException(status_code=400, detail="No images provided")
    binaries = [await upload.read() for upload in files]
    try:
        return await manager.add_reference_images(station_config, model_name, binaries)
    except ModelNotInConfigError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Model server error: {e}")


@router.get(
    "/models/{model_name}/reference-images/jobs/{job_id}",
    summary="Progress of a reference-image fit",
)
async def get_reference_images_job(
    model_name: str,
    job_id: str,
    manager: IModelTrainerManager = Depends(get_model_trainer_manager),
    station_config: StationConfig = Depends(get_config),
) -> TrainingJob:
    try:
        return await manager.get_training_job(station_config, model_name, job_id)
    except ModelNotInConfigError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Model server error: {e}")
