import io
from pathlib import Path
from typing import Dict

import aiohttp
import requests
import numpy as np
from PIL import Image

from edge_orchestrator import logger
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.ports.model_forward import ModelForward

import base64
import json
import copy

class TorchServingDetectionClassificationWrapper(ModelForward):

    def __init__(self, base_url, class_names_path: Path, image_shape=None):
        self.base_url = base_url
        self.class_names_path = class_names_path
        self.image_shape = image_shape

    async def perform_inference(self, model: ModelInfos, binary_data: bytes, binary_name: str) -> Dict[str, Dict]:
        processed_img = self.perform_pre_processing(binary_data)
        logger.debug(f'Processed image size: {processed_img.shape}')
        payload = {'data': base64.b64encode(binary_data)}
        model_url = f'{self.base_url}/predictions/{model.name}'

        try:
            response = requests.post(model_url, data=payload)
            json_data = response.json()
            logger.info(f'response received {json_data}')
            if len(json_data) == 0:
                return 'NO_DECISION'
            inference_output = self.perform_post_processing(model, json_data)
            return inference_output
        except Exception as e:
            logger.exception(e)
            inference_output = 'NO_DECISION'
            return inference_output

    def perform_pre_processing(self, binary: bytes):
        img = Image.open(io.BytesIO(binary))
        img = np.asarray(img)
        self.image_shape = img.shape[:2]
        return img

    def perform_post_processing(self, model: ModelInfos, json_outputs: dict) -> dict:
        inference_output = {}
        class_names = []
        if model.boxes_coordinates == None:
            json_outputs_copy = copy.deepcopy(json_outputs)
            for row in json_outputs_copy:
                row.pop(model.objectness_scores, None)
                row.pop(model.detection_classes, None)
            boxes_coordinates = np.array([list(row.values()) for row in json_outputs_copy])
        else:
            boxes_coordinates = [row[model.boxes_coordinates] for row in json_outputs],

        objectness_scores, detection_classes = (
            [row[model.objectness_scores] for row in json_outputs],
            [row[model.detection_classes] for row in json_outputs]
        )

        try:
            class_names = [c.strip() for c in open(self.class_names_path).readlines()]
        except Exception as e:
            logger.exception(e)
            logger.info('cannot open class names files at location {}'.format(self.class_names_path))

        for box_index, box_coordinates_in_current_image in enumerate(boxes_coordinates):
            # crop_image expects the box coordinates to be (xmin, ymin, xmax, ymax)
            # Mobilenet returns the coordinates as (ymin, xmin, ymax, xmax)
            # Hence, the switch here
            logger.info(f"box {box_coordinates_in_current_image} - image {self.image_shape}")

            height = self.image_shape[0]
            width = self.image_shape[1]
            original_dims = np.array([width, height, width, height])
            # box_coordinates_in_current_image = box_coordinates_in_current_image * original_dims
            box_coordinates_in_current_image = box_coordinates_in_current_image.astype(float).tolist()

            box_objectness_score_in_current_image = objectness_scores[box_index]

            boxes_detected_in_current_image_labels = detection_classes[box_index]

            if box_objectness_score_in_current_image >= model.objectness_threshold:
                inference_output[f'object_{box_index + 1}'] = {
                    'location': box_coordinates_in_current_image,
                    'score': box_objectness_score_in_current_image,
                    'label': boxes_detected_in_current_image_labels
                }

        return inference_output