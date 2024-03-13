import logging
from typing import Union, Any, List, Dict, AnyStr

import numpy as np
from fastapi import APIRouter, HTTPException, Request

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
            input_data = payload[b"inputs"]
            input_array = np.array(input_data, dtype=input_dtype)
            input_array /= 255

            interpreter.set_tensor(input_details[0]["index"], input_array)
            interpreter.invoke()

            output_tensor = interpreter.get_tensor(output_details[0]["index"])
            output_shape = output_details[0]['shape']
            outputs = np.reshape(output_tensor, output_shape)[0]

            temp_output = []
            for i in range(len(outputs[0]), 0, -1):
                temp_output.append(list(map(lambda x: x[i-1], outputs)))
            outputs = np.array(temp_output)

            # Computing 
            rows = outputs.shape[0]
            boxes = []
            scores = []
            class_ids = []

            for i in range(rows):
                classes_scores = outputs[i][4:]
                max_score, max_class_id = max((v, i) for i, v in enumerate(classes_scores))

                box = [float(outputs[i][0] - (0.5 * outputs[i][2])), float(outputs[i][1] - (0.5 * outputs[i][3])), 
                       float(outputs[i][0] + (0.5 * outputs[i][2])), float(outputs[i][1] + (0.5 * outputs[i][3]))] 
                boxes.append(box)
                scores.append(float(max_score)) 
                class_ids.append(float(max_class_id))

            boxes, scores, class_ids = nms(boxes, scores, class_ids)
            severities = compute_severities(input_array[0], boxes)

            prediction = {
                "outputs": {
                    "detection_boxes": [boxes],
                    "detection_classes": [class_ids],
                    "detection_scores": [scores],
                    "severities": [severities]
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


def compute_severities(image: np.array, boxes: List):
    severities = []
    for box in boxes:
        severities.append(compute_box_severity(image, box))
    return severities


def compute_box_severity(image: np.array, box: List):
    x1_pixel_index = int(box[0] * len(image))
    y1_pixel_index = int(box[1] * len(image[0]))
    x2_pixel_index = int(box[2] * len(image))
    y2_pixel_index = int(box[3] * len(image[0]))

    # Reshape to only the pixels in the detection box & as a list of pixels instead of a 2D array of them
    image_detection = image[x1_pixel_index:x2_pixel_index, y1_pixel_index:y2_pixel_index, :]
    image_detection = image_detection.reshape(-1, 3)
    number_of_pixels_in_box = image_detection.shape[0]

    # Filtering out light pixels
    mask_dark_pixels = np.all(image_detection < 0.5, axis=1)
    # Looking at severity as mean darkness
    dark_colors = image_detection[mask_dark_pixels].flatten()
    if dark_colors.size == 0:
        return 0.09
    else:
        ratio_pixel_dark_box = len(dark_colors) / 3 / number_of_pixels_in_box
        grade_dark_pixels_amount = 3 ** (ratio_pixel_dark_box - 1)
        grade_mean_darkness = (0.5 - dark_colors.mean()) * 2

        severity = round(0.8 * grade_mean_darkness + 0.2 * grade_dark_pixels_amount, 2)
        return severity


def nms(boxes, scores, class_ids, score_threshold=0.4, iou_threshold=0.45):
    non_max_suppression_parameters_checks(score_threshold, iou_threshold)

    nms_result_boxes = []
    nms_result_scores = []
    nms_result_classes = []

    # Cut values with low confidence
    scores = np.array(scores)
    mask_low_confidence = scores > score_threshold
    scores = scores[mask_low_confidence].tolist()
    boxes = np.array(boxes)[mask_low_confidence].tolist()
    class_ids = np.array(class_ids)[mask_low_confidence].tolist()

    # Performing the Non-max suppression loop
    while len(boxes) != 0:
        delete_index_list = []

        # Locating & Saving max confidence box
        highest_confidence_index = scores.index(max(scores))
        highest_confidence_box = boxes[highest_confidence_index]

        nms_result_boxes.append(highest_confidence_box)
        nms_result_scores.append(scores[highest_confidence_index])
        nms_result_classes.append(class_ids[highest_confidence_index])
        delete_index_list.append(highest_confidence_index)

        # Iterating to analyse the iou scores
        for index_box, box in enumerate(boxes):
            iou = compute_iou(highest_confidence_box, box)
            if iou > iou_threshold:
                delete_index_list.append(index_box)

        # Rebuild the box list to remove the boxes that were close to the last max score
        boxes = [box for index_box, box in enumerate(boxes) if index_box not in delete_index_list]
        scores = [score for index_score, score in enumerate(scores) if index_score not in delete_index_list]
        class_ids = [class_id for index_class, class_id in enumerate(class_ids) if index_class not in delete_index_list]

    return nms_result_boxes, nms_result_scores, nms_result_classes


def non_max_suppression_parameters_checks(conf_thres, iou_thres):
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'


def compute_iou(box1, box2):
    box1_width = box1[2] - box1[0]
    box1_height = box1[3] - box1[1]
    box2_width = box2[2] - box2[0]
    box2_height = box2[3] - box2[1]

    # Check if centers of boxes are close enough to be intersected
    if ((abs((box1[0] + box1_width/2) - (box2[0] + box2_width / 2)) < 0.5 * (box2_width + box1_width)) &
            (abs((box1[1] + box1_height/2) - (box2[1] + box2_height / 2)) < 0.5 * (box2_height + box1_height))):
        intersection_area = (max(box1[2], box2[2]) - min(box1[0], box2[0])) * (max(box1[3], box2[3]) - min(box1[1], box2[1]))
        union_area = box1_width * box1_height + box2_width * box2_height - intersection_area
        return intersection_area / union_area
    return 0
