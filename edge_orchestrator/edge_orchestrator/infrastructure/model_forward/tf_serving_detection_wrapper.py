import io
from pathlib import Path
from typing import Dict

import aiohttp
import numpy as np
from PIL import Image

from edge_orchestrator import logger
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.ports.model_forward import ModelForward


class TFServingDetectionWrapper(ModelForward):

    def __init__(self, base_url, class_names_path: Path, image_shape=None):
        self.base_url = base_url
        self.class_names_path = class_names_path
        self.image_shape = image_shape

    async def perform_inference(self, model: ModelInfos, binary_data: bytes, binary_name: str) -> Dict[str, Dict]:
        processed_img = self.perform_pre_processing(model, binary_data)
        logger.debug(f'Processed image size: {processed_img.shape}')
        payload = {'inputs': processed_img.tolist()}
        model_url = f'{self.base_url}/v1/models/{model.name}/versions/{model.version}:predict'
        logger.info(f'Get prediction at {model_url}')
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

    def perform_pre_processing(self, model: ModelInfos, binary: bytes):
        img = Image.open(io.BytesIO(binary))
        img_array = np.asarray(img)
        self.image_shape = img_array.shape[:2]
        resized_image = img.resize((model.image_resolution[0], model.image_resolution[1]), Image.ANTIALIAS)
        img = np.expand_dims(resized_image, axis=0).astype(np.uint8)
        return img

    def perform_post_processing(self, model: ModelInfos, json_outputs: dict) -> dict:
        inference_output = {}

        boxes_coordinates, objectness_scores, detection_classes = (
            json_outputs[model.boxes_coordinates][0],
            json_outputs[model.objectness_scores][0],
            json_outputs[model.detection_classes][0]
        )

        try:
            class_names = [c.strip() for c in open(self.class_names_path).readlines()]
        except Exception as e:
            logger.exception(e)
            logger.info('cannot open class names files at location {}'.format(self.class_names_path))

        for class_to_detect in model.class_to_detect:
            class_to_detect_position = np.where(np.array(class_names) == class_to_detect)
            detection_class_positions = np.where(np.array(detection_classes) == float(class_to_detect_position[0] + 1))

            for box_index in detection_class_positions[0]:
                box_coordinates_in_current_image = boxes_coordinates[box_index]
                image_height = self.image_shape[0]
                image_width = self.image_shape[1]

                # Mobilenet returns the coordinates as (ymin, xmin, ymax, xmax)
                y_min = int(float(box_coordinates_in_current_image[0]) * image_height)
                x_min = int(float(box_coordinates_in_current_image[1]) * image_width)
                y_max = int(float(box_coordinates_in_current_image[2]) * image_height)
                x_max = int(float(box_coordinates_in_current_image[3]) * image_width)

                # crop_image expects the box coordinates to be (xmin, ymin, xmax, ymax)
                box_coordinates_in_current_image = [x_min, y_min, x_max, y_max]
                box_objectness_score_in_current_image = objectness_scores[box_index]

                if box_objectness_score_in_current_image >= model.objectness_threshold:
                    inference_output[f'object_{box_index + 1}'] = {
                        'label': class_to_detect,
                        'location': box_coordinates_in_current_image,
                        'score': box_objectness_score_in_current_image
                    }
        return inference_output
