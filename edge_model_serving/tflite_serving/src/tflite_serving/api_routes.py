import io
import io
import logging
from typing import Any, Dict, List, Optional, cast

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from PIL import Image

from tflite_serving.schemas import (
    ClassificationPrediction,
    DetectedObject,
    DetectionPrediction,
    ModelMetadataResponse,
    PredictionResponse,
)
from tflite_serving.utils.yolo_postprocessing import (
    compute_severities,
    non_max_suppression,
    yolo_extract_boxes_information,
)

api_router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preprocess(
    image: Image.Image,
    input_shape: List[int],
    input_dtype: Any,
    normalization: str,
) -> np.ndarray:
    """Resize, reformat, and normalize an image to match the model's expected input."""
    _, height, width, channels = input_shape
    image = image.convert("L" if channels == 1 else "RGB")
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    arr = np.array(image, dtype=np.float32)
    if normalization == "mobilenet":
        arr = (arr / 127.0) - 1.0
    elif normalization == "yolo":
        arr = arr / 255.0
    # "uint8" → no normalization, cast to target dtype below
    arr = np.expand_dims(arr, axis=0).astype(input_dtype)
    return arr


def _postprocess_classification(
    outputs: List[np.ndarray], class_names: List[str]
) -> ClassificationPrediction:
    scores = outputs[0][0]
    best_idx = int(np.argmax(scores))
    return ClassificationPrediction(
        prediction_type="class",
        label=class_names[best_idx],
        probability=round(float(scores[best_idx]), 5),
    )


def _postprocess_object_detection(
    outputs: List[np.ndarray], class_names: List[str]
) -> DetectionPrediction:
    boxes = outputs[0]
    classes = outputs[1].astype(int)
    scores = outputs[2]

    detected_objects: Dict[str, DetectedObject] = {}
    for i, (box, cls, score) in enumerate(zip(boxes[0], classes[0], scores[0])):
        label = class_names[cls] if cls < len(class_names) else str(cls)
        detected_objects[f"object_{i + 1}"] = DetectedObject(
            location=[round(c, 4) for c in box.tolist()],
            objectness=round(float(score), 5),
            label=label,
        )
    return DetectionPrediction(
        prediction_type="objects", detected_objects=detected_objects
    )


def _postprocess_yolo(
    outputs: List[np.ndarray], class_names: List[str], input_array: np.ndarray
) -> DetectionPrediction:
    raw = outputs[0][0]
    # Rotate the YOLO output tensor
    rotated = []
    for i in range(len(raw[0]), 0, -1):
        rotated.append([x[i - 1] for x in raw])
    rotated = np.array(rotated)

    boxes, scores, class_ids = yolo_extract_boxes_information(rotated)
    boxes, scores, class_ids = non_max_suppression(boxes, scores, class_ids)
    severities = compute_severities(input_array[0], boxes)

    detected_objects: Dict[str, DetectedObject] = {}
    for i, (box, score, cls_id, severity) in enumerate(
        zip(boxes, scores, class_ids, severities)
    ):
        label = (
            class_names[int(cls_id)]
            if int(cls_id) < len(class_names)
            else str(int(cls_id))
        )
        detected_objects[f"object_{i + 1}"] = DetectedObject(
            location=[round(c, 4) for c in box],
            objectness=round(float(score), 5),
            label=label,
            severity=severity,
        )
    return DetectionPrediction(
        prediction_type="objects", detected_objects=detected_objects
    )


def _get_state(request: Any) -> tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """Extract typed model registries from app state.

    ``request`` is typed ``Any`` because ``Request.app`` is ``ASGIApp`` in
    Starlette's stubs and does not expose ``.state`` — this is a known
    Starlette limitation with no clean typing solution at call-site level.
    """
    interpreters = cast(Dict[str, Any], request.app.state.model_interpreters)
    metadata_registry = cast(
        Dict[str, Dict[str, Any]], request.app.state.model_metadata
    )
    return interpreters, metadata_registry


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@api_router.get("/")
async def info() -> str:
    return "tflite-server docs at ip:port/docs"


@api_router.get("/models")
async def get_models(request: Request) -> List[str]:
    interpreters, _ = _get_state(request)
    return list(interpreters.keys())


@api_router.get(
    "/models/{model_name}/metadata",
    response_model=ModelMetadataResponse,
)
async def get_model_metadata(
    model_name: str, request: Request
) -> ModelMetadataResponse:
    interpreters, metadata_registry = _get_state(request)
    if model_name not in interpreters:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    interpreter = interpreters[model_name]
    input_details: List[Dict[str, Any]] = interpreter.get_input_details()
    metadata: Dict[str, Any] = metadata_registry.get(model_name, {})
    return ModelMetadataResponse(
        input_shape=input_details[0]["shape"].tolist(),
        input_dtype=np.dtype(input_details[0]["dtype"]).name,
        output_type=metadata.get("output_type"),
        class_names=metadata.get("class_names"),
        normalization=metadata.get("normalization"),
    )


@api_router.post(
    "/models/{model_name}/versions/{model_version}:predict",
    response_model=PredictionResponse,
    response_model_exclude_none=True,
)
async def predict(
    model_name: str, model_version: str, request: Request  # noqa: ARG001
) -> PredictionResponse:
    interpreters, metadata_registry = _get_state(request)
    if model_name not in interpreters:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    interpreter = interpreters[model_name]
    metadata: Dict[str, Any] = metadata_registry.get(model_name, {})
    output_type: Optional[str] = metadata.get("output_type")
    class_names: List[str] = metadata.get("class_names", [])
    normalization: str = metadata.get("normalization", "uint8")

    if output_type is None:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No metadata.json found for model '{model_name}'. "
                "Add a metadata.json alongside the .tflite file to enable inference."
            ),
        )

    input_details: List[Dict[str, Any]] = interpreter.get_input_details()
    output_details: List[Dict[str, Any]] = interpreter.get_output_details()
    input_shape: List[int] = input_details[0]["shape"].tolist()
    input_dtype: Any = input_details[0]["dtype"]

    logging.info(
        f"Predicting with '{model_name}' | shape={input_shape} | output_type={output_type}"
    )

    try:
        body: bytes = await request.body()
        if not body:
            raise HTTPException(
                status_code=400, detail="Empty request body — expected raw image bytes"
            )

        image = Image.open(io.BytesIO(body))
        input_array = _preprocess(image, input_shape, input_dtype, normalization)

        interpreter.set_tensor(input_details[0]["index"], input_array)
        interpreter.invoke()
        outputs: List[np.ndarray] = [
            interpreter.get_tensor(d["index"]) for d in output_details
        ]

        if output_type == "classification":
            return _postprocess_classification(outputs, class_names)
        elif output_type == "object_detection":
            return _postprocess_object_detection(outputs, class_names)
        elif output_type == "yolo":
            return _postprocess_yolo(outputs, class_names, input_array)
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown output_type '{output_type}' in metadata.json for model '{model_name}'.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Prediction error for model '{model_name}'")
        logging.exception(f"Prediction error for model '{model_name}'")
        raise HTTPException(status_code=500, detail=str(e))
