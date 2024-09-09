import logging
import sys
from typing import Union, Any, List, Dict, AnyStr

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from tflite_serving.utils.yolo_postprocessing import (
    yolo_extract_boxes_information,
    non_max_suppression,
    compute_severities,
)
from tflite_serving.utils.st_yolo_postprocessing import tiny_yolo_v2_decode, tiny_yolo_v2_nms, ANCHORS, NUM_CLASSES

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

    # logging.info(f"interpreting with {model_name} for input type {input_dtype}")
    print(f"interpreting with {model_name} for input type {input_dtype}")
    print("input details :", input_details)
    # logging.warning(f"output details: {output_details}")
    print(f"output details: {output_details}")

    try:
        input_data = payload[b"inputs"]
        input_array = None
        model_type = None
        if b"model_type" in payload.keys():
            model_type = payload[b"model_type"]
            if model_type == "yolo":
                print("model type is yolo")
                input_array = np.array(input_data)
                input_array = (input_array / input_details[0]['quantization'][0]) + input_details[0]['quantization'][1]
                input_array = np.clip(np.round(input_array), np.iinfo(input_details[0]['dtype']).min,
                                      np.iinfo(input_details[0]['dtype']).max)
                input_array = input_array.astype(input_details[0]['dtype'])
            else:
                input_array = np.array(input_data, dtype=input_dtype)

        #debug
        print(f"input array type: {input_array.dtype}")
        print(f"input array shape: {input_array.shape}")

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
                    "severities": [None],
                }
            }
        elif model_type == "yolo":
            INPUT_SHAPE = (256, 256)
            output_data = [interpreter.get_tensor(output_details[j]["index"]) for j in range(len(output_details))]
            decoded_output = tiny_yolo_v2_decode(output_data[0], ANCHORS, NUM_CLASSES, np.array(INPUT_SHAPE))
            for i, tensor in enumerate(decoded_output):
                print(f"Decoded output part {i} shape: {tensor.shape}")
                print(f"Decoded output part {i} data: {tensor}")

            boxes, scores, classes, my_boxes = tiny_yolo_v2_nms(decoded_output, np.array(INPUT_SHAPE))
            print("Filtered boxes:", boxes)
            print("Scores:", scores)
            print("Classes:", classes)

            prediction = {
                "outputs": {
                    "detection_boxes": boxes.numpy().tolist(),
                    "detection_classes": classes.numpy().tolist(),
                    "detection_scores": scores.numpy().tolist(),
                    "severities": [None],
                }
            }
            print(prediction)
            print("after yolo loop")

        elif len(output_details) == 1:
            scores = interpreter.get_tensor(output_details[0]["index"])
            logging.warning(
                f"interpreting with {model_name} for input type {input_dtype}"
            )
            logging.warning(f"Scores of classification: {scores[0]}")
            prediction = {"outputs": scores.tolist()}

        print("enf of predict")
        return prediction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
