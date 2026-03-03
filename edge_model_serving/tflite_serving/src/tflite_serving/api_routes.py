import io
import logging
from typing import List

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from PIL import Image

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
    image: Image.Image, input_shape: list, input_dtype, normalization: str
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


def _postprocess_classification(outputs: list, class_names: List[str]) -> dict:
    scores = outputs[0][0]
    best_idx = int(np.argmax(scores))
    return {
        "prediction_type": "class",
        "label": class_names[best_idx],
        "probability": round(float(scores[best_idx]), 5),
    }


def _postprocess_object_detection(outputs: list, class_names: List[str]) -> dict:
    boxes = outputs[0]
    classes = outputs[1].astype(int)
    scores = outputs[2]

    detected_objects = {}
    for i, (box, cls, score) in enumerate(zip(boxes[0], classes[0], scores[0])):
        label = class_names[cls] if cls < len(class_names) else str(cls)
        detected_objects[f"object_{i + 1}"] = {
            "location": [round(c, 4) for c in box.tolist()],
            "objectness": round(float(score), 5),
            "label": label,
        }
    return {"prediction_type": "objects", "detected_objects": detected_objects}


def _postprocess_yolo(
    outputs: list, class_names: List[str], input_array: np.ndarray
) -> dict:
    raw = outputs[0][0]
    # Rotate the YOLO output tensor
    rotated = []
    for i in range(len(raw[0]), 0, -1):
        rotated.append([x[i - 1] for x in raw])
    rotated = np.array(rotated)

    boxes, scores, class_ids = yolo_extract_boxes_information(rotated)
    boxes, scores, class_ids = non_max_suppression(boxes, scores, class_ids)
    severities = compute_severities(input_array[0], boxes)

    detected_objects = {}
    for i, (box, score, cls_id, severity) in enumerate(
        zip(boxes, scores, class_ids, severities)
    ):
        label = (
            class_names[int(cls_id)]
            if int(cls_id) < len(class_names)
            else str(int(cls_id))
        )
        detected_objects[f"object_{i + 1}"] = {
            "location": [round(c, 4) for c in box],
            "objectness": round(float(score), 5),
            "label": label,
            "severity": severity,
        }
    return {"prediction_type": "objects", "detected_objects": detected_objects}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@api_router.get("/")
async def info():
    return "tflite-server docs at ip:port/docs"


@api_router.get("/models")
async def get_models(request: Request):
    return list(request.app.state.model_interpreters.keys())


@api_router.get("/models/{model_name}/metadata")
async def get_model_metadata(model_name: str, request: Request):
    if model_name not in request.app.state.model_interpreters:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    interpreter = request.app.state.model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    metadata = request.app.state.model_metadata.get(model_name, {})
    return {
        "input_shape": input_details[0]["shape"].tolist(),
        "input_dtype": np.dtype(input_details[0]["dtype"]).name,
        **metadata,
    }


@api_router.post("/models/{model_name}/versions/{model_version}:predict")
async def predict(model_name: str, model_version: str, request: Request):
    if model_name not in request.app.state.model_interpreters:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    interpreter = request.app.state.model_interpreters[model_name]
    metadata = request.app.state.model_metadata.get(model_name, {})
    output_type = metadata.get("output_type")
    class_names = metadata.get("class_names", [])
    normalization = metadata.get("normalization", "uint8")

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]["shape"].tolist()
    input_dtype = input_details[0]["dtype"]

    logging.info(
        f"Predicting with '{model_name}' | shape={input_shape} | output_type={output_type}"
    )

    try:
        body = await request.body()
        if not body:
            raise HTTPException(
                status_code=400, detail="Empty request body — expected raw image bytes"
            )

        image = Image.open(io.BytesIO(body))
        input_array = _preprocess(image, input_shape, input_dtype, normalization)

        interpreter.set_tensor(input_details[0]["index"], input_array)
        interpreter.invoke()
        outputs = [interpreter.get_tensor(d["index"]) for d in output_details]

        if output_type == "classification":
            return _postprocess_classification(outputs, class_names)
        elif output_type == "object_detection":
            return _postprocess_object_detection(outputs, class_names)
        elif output_type == "yolo":
            return _postprocess_yolo(outputs, class_names, input_array)
        else:
            # Fallback heuristic for models without metadata
            logging.warning(
                f"No output_type in metadata for '{model_name}', falling back to heuristic"
            )
            if len(output_details) >= 3:
                return _postprocess_object_detection(outputs, class_names)
            return {"prediction_type": "class", "raw_outputs": outputs[0].tolist()}

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Prediction error for model '{model_name}'")
        raise HTTPException(status_code=500, detail=str(e))
