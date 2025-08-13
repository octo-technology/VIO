import logging
from typing import Any, AnyStr, Dict, List, Union, Tuple
import numpy as np
from fastapi import APIRouter, HTTPException, Request
import time
import os
from PIL import Image
from pathlib import Path


from utils.yolo11n_postprocessing import (
    compute_severities,
    non_max_suppression,
    yolo_extract_boxes_information,
)

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

api_router = APIRouter()


# Page initiale
@api_router.get("/")
async def info():
    return """Welcome to the onnx-server for VIO !!"""


# Lister les modèles ONNX chargés
@api_router.get("/models")
async def get_models(request: Request) -> List[str]:
    return list(
        request.app.state.model_interpreters.keys()
    )  # Retourne les modèles disponibles


# Récupérer les métadonnées d’un modèle
@api_router.get("/models/{model_name}/versions/{model_version}/resolution")
async def get_model_metadata(
    model_name: str, model_version: str, request: Request
) -> Dict[str, Tuple]:
    session = request.app.state.model_interpreters[model_name]
    input_details = session.get_inputs()
    return {"inputs_shape": input_details[0].shape}


# Faire une prédictionPrediction


def load_test_image(path: str) -> np.ndarray:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image de test introuvable : {path}")
    img = Image.open(path).convert("RGB")
    img = img.resize((640, 640))
    arr = np.array(img, dtype=np.float32) / 255.0  # Normalization : [640,640,3]
    arr = arr.transpose(2, 0, 1)  # --> [3,640,640]
    arr = np.expand_dims(arr, axis=0)  # --> [1,3,640,640] : format accepté par YOLO
    return arr


# Modifier l'endpoint pour que l'utilisateur puisse envoyer une image par la requete
@api_router.post("/models/{model_name}/versions/{model_version}:predict")
async def predict_test_image(model_name: str, model_version: str, request: Request):
    HERE = Path(__file__).resolve().parent

    # verification modèle
    if model_name not in request.app.state.model_interpreters:
        raise HTTPException(status_code=404, detail="Modèle non trouvé")
    session = request.app.state.model_interpreters[
        model_name
    ]  # recuperer la session d'inference du modèle

    # charger l'image
    try:
        test_img_path = HERE / "data" / "test_img.jpg"
        input_array = load_test_image(test_img_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    logging.info(f"Chargé image de test, forme finale {input_array.shape}")

    # inférence
    try:
        input_details = session.get_inputs()
        ort_inputs = {input_details[0].name: input_array}
        outputs = session.run(None, ort_inputs)
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur d'inférence ONNX")

    # Post‐processing
    try:
        outputs = outputs[0][0]
        boxes, scores, class_ids = yolo_extract_boxes_information(outputs)
        boxes, scores, class_ids = non_max_suppression(boxes, scores, class_ids)
        severities = compute_severities(input_array[0], boxes)

        prediction = {
            "outputs": {
                "detection_boxes": [boxes.tolist()],
                "detection_classes": [class_ids.tolist()],
                "detection_scores": [scores.tolist()],
                "severities": [severities],
            }
        }
        return prediction
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur postprocessing")


@api_router.post("/models/{model_name}/performance")
async def model_performance(model_name: str, request: Request):

    # Verif exsitence modele
    if model_name not in request.app.state.model_interpreters:
        raise HTTPException(status_code=404, detail="Modèle non trouvé")
    session = request.app.state.model_interpreters[model_name]
    input_details = session.get_inputs()

    # get img
    HERE = Path(__file__).resolve().parent
    test_img_path = HERE / "data" / "test_img.jpg"
    try:
        input_array = load_test_image(test_img_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Verif format attendu par YOLO
    if input_array.shape != (1, 3, 640, 640):
        raise HTTPException(
            status_code=400,
            detail=f"Les dimensions de l'input doivent être [1,3,640,640], got {input_array.shape}",
        )

    # Inférence + mesure du temps
    try:
        ort_inputs = {input_details[0].name: input_array}
        start = time.time()
        _ = session.run(None, ort_inputs)
        exec_time = time.time() - start
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur d'inférence ONNX")

    return {
        "model_name": model_name,
        "input_shape": input_array.shape,
        "inference_time_sec": round(exec_time, 4),
    }
