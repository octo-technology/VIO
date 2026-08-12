import io
import logging
from typing import Any, Dict, List, cast

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from PIL import Image

from anomaly_serving.fit_jobs import serialize_job, start_fit_job
from anomaly_serving.preprocessing import preprocess_image
from anomaly_serving.rad_model.decision import (
    compute_score,
    decide,
    normalize_confidence,
)
from anomaly_serving.rad_model.rad import RAD
from anomaly_serving.rad_registry import get_models_path, resolve_serving_config
from anomaly_serving.schemas import (
    AnomalyPrediction,
    FitJobAccepted,
    FitJobStatus,
    ModelMetadataResponse,
)

api_router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_state(request: Any) -> tuple[Dict[str, RAD], Dict[str, Dict[str, Any]]]:
    """Extract typed model registries from app state.

    ``request`` is typed ``Any`` because ``Request.app`` is ``ASGIApp`` in
    Starlette's stubs and does not expose ``.state`` — this is a known
    Starlette limitation with no clean typing solution at call-site level.
    """
    models = getattr(request.app.state, "rad_models", None)
    metadata_registry = getattr(request.app.state, "model_metadata", None)
    if models is None or metadata_registry is None:
        raise HTTPException(status_code=503, detail="Server is starting up — model registry not ready yet")
    return cast(Dict[str, RAD], models), cast(Dict[str, Dict[str, Any]], metadata_registry)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@api_router.get("/")
async def info() -> str:
    return "rad-server docs at ip:port/docs"


@api_router.get("/models")
async def get_models(request: Request) -> List[str]:
    models, _ = _get_state(request)
    return list(models.keys())


@api_router.get("/capabilities")
async def get_capabilities(request: Request) -> Dict[str, Any]:
    models, metadata_registry = _get_state(request)
    capabilities = {}
    for model_name in models:
        metadata = metadata_registry.get(model_name, {})
        capabilities[model_name] = {
            "version": str(metadata.get("version", "1")),
            "output_type": metadata.get("output_type"),
            "class_names": metadata.get("class_names"),
        }
    return {"models": capabilities}


@api_router.get(
    "/models/{model_name}/metadata",
    response_model=ModelMetadataResponse,
)
async def get_model_metadata(model_name: str, request: Request) -> ModelMetadataResponse:
    models, metadata_registry = _get_state(request)
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    model = models[model_name]
    metadata: Dict[str, Any] = metadata_registry.get(model_name, {})
    config = resolve_serving_config(metadata)
    return ModelMetadataResponse(
        version=str(metadata.get("version", "1")),
        # Images are normalised server-side, so the wire format is raw uint8 RGB.
        input_shape=[1, config["resize"], config["resize"], 3],
        input_dtype="uint8",
        output_type=metadata.get("output_type"),
        class_names=metadata.get("class_names"),
        normalization=metadata.get("normalization"),
        backbone=model.backbone,
        resize=config["resize"],
        decision_method=config["decision_method"],
        decision_param=config["decision_param"],
        threshold=config["threshold"],
    )


@api_router.post(
    "/models/{model_name}/versions/{model_version}:predict",
    response_model=AnomalyPrediction,
)
async def predict(
    model_name: str,
    model_version: str,
    request: Request,
) -> AnomalyPrediction:
    models, metadata_registry = _get_state(request)
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    model = models[model_name]
    config = resolve_serving_config(metadata_registry.get(model_name, {}))

    logging.info(
        f"Predicting with '{model_name}' | resize={config['resize']} | "
        f"decision={config['decision_method']}({config['decision_param']}) | "
        f"threshold={config['threshold']}"
    )

    try:
        body: bytes = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Empty request body — expected raw image bytes")

        image = Image.open(io.BytesIO(body))
        input_tensor = preprocess_image(image, config["resize"])

        # RAD also returns its own image score, computed with the fit-time
        # aggregation; it is discarded so the decision method stays a
        # serving-side setting driven by metadata.json.
        _, anomaly_maps = model.predict(input_tensor)

        raw_score = compute_score(anomaly_maps[0], config["decision_method"], config["decision_param"])
        threshold = config["threshold"]

        return AnomalyPrediction(
            prediction_type="class",
            label=decide(raw_score, threshold),
            probability=round(normalize_confidence(raw_score, threshold), 5),
            raw_score=round(raw_score, 6),
            decision_method=config["decision_method"],
            decision_param=config["decision_param"],
            threshold=threshold,
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Prediction error for model '{model_name}'")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Reference images / memory bank
# ---------------------------------------------------------------------------


@api_router.post(
    "/models/{model_name}/reference-images",
    status_code=202,
    response_model=FitJobAccepted,
)
async def add_reference_images(
    model_name: str,
    request: Request,
    files: List[UploadFile] = File(default=[]),
) -> FitJobAccepted:
    """Extend a model's anomaly-free memory bank with more normal images.

    The fit runs in the background and the bank is persisted to disk, so a
    later restart loads it without re-fitting. Poll the returned job for
    progress.
    """
    models, metadata_registry = _get_state(request)
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    if not files:
        raise HTTPException(status_code=400, detail="No images provided")

    fitting_models = getattr(request.app.state, "fitting_models", set())
    if model_name in fitting_models:
        raise HTTPException(
            status_code=409,
            detail=f"A fit for model '{model_name}' is already running",
        )

    config = resolve_serving_config(metadata_registry.get(model_name, {}))
    images_bytes = [await upload.read() for upload in files]
    ckpt_path = get_models_path() / model_name / "model.ckpt"

    job = start_fit_job(
        request.app,
        model_name=model_name,
        model=models[model_name],
        images_bytes=images_bytes,
        resize=config["resize"],
        ckpt_path=ckpt_path,
    )
    return FitJobAccepted(job_id=job["job_id"], total=job["total"], status=job["status"])


@api_router.get(
    "/models/{model_name}/reference-images/jobs/{job_id}",
    response_model=FitJobStatus,
)
async def get_reference_images_job(model_name: str, job_id: str, request: Request) -> FitJobStatus:
    jobs = getattr(request.app.state, "fit_jobs", {})
    job = jobs.get(job_id)
    if job is None or job["model_name"] != model_name:
        raise HTTPException(status_code=404, detail=f"No fit job '{job_id}' for model '{model_name}'")
    return FitJobStatus(**serialize_job(job))
