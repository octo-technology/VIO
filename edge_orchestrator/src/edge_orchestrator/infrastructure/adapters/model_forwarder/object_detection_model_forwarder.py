import io
import logging
from typing import Any, Dict

import aiohttp
import numpy as np
from PIL import Image

from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class ObjectDetectionModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        width = self._model_forwarder_config.expected_image_resolution.width
        height = self._model_forwarder_config.expected_image_resolution.height
        image = Image.open(io.BytesIO(binary))
        resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
        image_array = np.asarray(resized_image)
        return np.expand_dims(image_array, axis=0).astype(np.uint8)[:, :, :, :3]

    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        model_type = None
        if self._model_forwarder_config.model_name == ModelName.yolo_coco_nano:
            model_type = "yolo"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._get_model_url(),
                json={
                    "inputs": preprocessed_binary.tolist(),
                    "model_type": model_type,
                },
            ) as response:
                return await response.json()

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        predictions = prediction_response["outputs"]
        if (
            "detection_boxes" not in predictions
            or "detection_scores" not in predictions
            or "detection_classes" not in predictions
            or len(predictions["detection_boxes"]) == 0
            or len(predictions["detection_scores"]) == 0
            or len(predictions["detection_classes"]) == 0
        ):
            self._logger.warning("No detected objects found!")
            return DetectionPrediction(prediction_type=PredictionType.objects, detected_objects={})

        detected_objects = {}
        boxes_coordinates, objectness_scores, detection_classes = (
            predictions["detection_boxes"][0],
            predictions["detection_scores"][0],
            predictions["detection_classes"][0],
        )
        class_names = self._get_class_names()

        for box_index in range(len(boxes_coordinates)):
            boxes_coordinates[box_index] = [round(coordinate, 4) for coordinate in boxes_coordinates[box_index]]
            box_objectness = objectness_scores[box_index]
            detected_objects[f"object_{box_index + 1}"] = DetectedObject(
                location=boxes_coordinates[box_index],
                objectness=box_objectness,
                label=class_names[int(detection_classes[box_index])],
            )
        return DetectionPrediction(prediction_type=PredictionType.objects, detected_objects=detected_objects)
