import logging
from typing import Union, Any, List, Dict, AnyStr

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from tflite_serving.utils.yolo_postprocessing import (
    yolo_extract_boxes_information,
    nms,
    compute_severities,
)

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

api_router = APIRouter()


@api_router.get("/")
async def info():
    return """tflite-server docs at ip:port/docs"""


@api_router.get("/models")
async def get_models(request: Request):
    return list(request.app.state.model_interpreters.keys())


@api_router.get("/models/{model_name}/versions/{model_version}/resolution")
async def get_model_metadata(model_name: str, model_version: str, request: Request):
    interpreter = request.app.state.model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    return {"inputs_shape": input_details[0]["shape"].tolist()}


@api_router.post("/models/{model_name}/versions/{model_version}:predict")
async def predict(
    model_name: str, model_version: str, payload: JSONStructure, request: Request
):
    interpreter = request.app.state.model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_dtype = input_details[0]["dtype"]
    logging.info(f"interpreting with {model_name} for input type {input_dtype}")
    logging.warning(f"output details: {output_details}")

    try:
        model_type = payload[b"model_type"]
        input_data = payload[b"inputs"]
        input_array = np.array(input_data, dtype=input_dtype)

        if model_type == "yolo":
            input_array /= 255

        interpreter.set_tensor(input_details[0]["index"], input_array)
        interpreter.invoke()
        # Process image and get predictions
        prediction = {}

        if len(output_details) >= 3:
            boxes = interpreter.get_tensor(output_details[0]["index"])
            classes = interpreter.get_tensor(output_details[1]["index"]).astype(int) + 1
            scores = interpreter.get_tensor(output_details[2]["index"])

            logging.warning(
                f"interpreting with {model_name} for input type {input_dtype}"
            )
            logging.warning(f"Boxes of object detected: {boxes[0]}")
            logging.warning(f"Classes of object detected: {classes[0]}")
            logging.warning(f"Scores of object detected: {scores[0]}")

            prediction = {
                "outputs": {
                    "detection_boxes": boxes.tolist(),
                    "detection_classes": classes.tolist(),
                    "detection_scores": scores.tolist(),
                }
            }
        elif model_type == "yolo":
            outputs = interpreter.get_tensor(output_details[0]["index"])[0]

            # Rotate the tensor
            temp_output = []
            for i in range(len(outputs[0]), 0, -1):
                temp_output.append(list(map(lambda x: x[i - 1], outputs)))
            outputs = np.array(temp_output)

            # Extracting the boxes information to select only the most relevant ones
            boxes, scores, class_ids = yolo_extract_boxes_information(outputs)
            boxes, scores, class_ids = nms(boxes, scores, class_ids)
            severities = compute_severities(input_array[0], boxes)

            prediction = {
                "outputs": {
                    "detection_boxes": [boxes],
                    "detection_classes": [class_ids],
                    "detection_scores": [scores],
                    "severities": [severities],
                }
            }

        elif len(output_details) == 1:
            scores = interpreter.get_tensor(output_details[0]["index"])
            logging.warning(
                f"interpreting with {model_name} for input type {input_dtype}"
            )
            logging.warning(f"Scores of classification: {scores[0]}")
            prediction = {"outputs": scores.tolist()}

        return prediction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
