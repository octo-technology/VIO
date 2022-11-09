import io
from pathlib import Path
from typing import Dict

import aiohttp
import numpy as np
from PIL import Image

from supervisor import logger
from supervisor.domain.models.model_infos import ModelInfos
from supervisor.domain.ports.model_forward import ModelForward


class TFServingDetectionClassificationWrapper(ModelForward):

    def __init__(self, base_url, class_names_path: Path, image_shape=None):
        self.base_url = base_url
        self.image_shape = image_shape
        self.class_names_path = class_names_path

    async def perform_inference(self, model: ModelInfos, binary_data: bytes, binary_name: str) -> Dict[str, Dict]:
        processed_img = self.perform_pre_processing(binary_data)
        logger.debug(f'Processed image size: {processed_img.shape}')
        payload = {'inputs': processed_img.tolist()}
        model_url = f'{self.base_url}/v1/models/{model.name}/versions/{model.version}:predict'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(model_url, json=payload) as response:
                    json_data = await response.json()
            logger.info('json DONE')
            inference_output = self.perform_post_processing(model, json_data['outputs'])
            return inference_output
        except Exception as e:
            logger.exception(e)
            inference_output = 'NO_DECISION'
            return inference_output

    def perform_pre_processing(self, binary: bytes):
        img = Image.open(io.BytesIO(binary))
        img = np.asarray(img)
        self.image_shape = img.shape[:2]
        img = np.expand_dims(img, axis=0).astype(np.uint8)
        return img

    def perform_post_processing(self, model: ModelInfos, json_outputs: dict) -> dict:
        inference_output = {}
        class_names = []
        boxes_coordinates, objectness_scores, number_of_boxes, detection_classes = (
            json_outputs[model.boxes_coordinates][0],
            json_outputs[model.objectness_scores][0],
            json_outputs[model.number_of_boxes][0],
            json_outputs[model.detection_classes][0])

        try:
            class_names = [c.strip() for c in open(self.class_names_path).readlines()]
        except Exception as e:
            logger.exception(e)
            logger.info('cannot open class names files at location {}'.format(self.class_names_path))

        for box_index in range(int(number_of_boxes)):
            box_coordinates_in_current_image = boxes_coordinates[box_index]
            # crop_image expects the box coordinates to be (xmin, ymin, xmax, ymax)
            # Mobilenet returns the coordinates as (ymin, xmin, ymax, xmax)
            # Hence, the switch here
            box_coordinates_in_current_image = [int(box_coordinates_in_current_image[1] * self.image_shape[1]),
                                                int(box_coordinates_in_current_image[0] * self.image_shape[0]),
                                                int(box_coordinates_in_current_image[3] * self.image_shape[1]),
                                                int(box_coordinates_in_current_image[2] * self.image_shape[0])
                                                ]
            box_objectness_score_in_current_image = objectness_scores[box_index]

            boxes_detected_in_current_image_labels = detection_classes[box_index]

            if box_objectness_score_in_current_image >= model.objectness_threshold:
                inference_output[f'object_{box_index + 1}'] = {
                    'location': box_coordinates_in_current_image,
                    'score': box_objectness_score_in_current_image,
                    'label': class_names[int(boxes_detected_in_current_image_labels)]
                }

        return inference_output
