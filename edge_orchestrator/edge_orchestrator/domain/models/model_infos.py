import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from edge_orchestrator.domain.ports.inventory import Inventory


class ModelInfos:
    def __init__(
        self,
        id: str,
        name: str,
        category: str,
        version: str,
        camera_id: str,
        depends_on: List[str] = [],
        image_resolution: Optional[List[int]] = None,
        class_names: Optional[List[str]] = None,
        boxes_coordinates: Optional[str] = None,
        objectness_scores: Optional[str] = None,
        number_of_boxes: Optional[str] = None,
        detection_classes: Optional[str] = None,
        class_to_detect: Optional[List[str]] = None,
        class_names_path: Optional[str] = None,
        objectness_threshold: Optional[float] = None,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.version = version
        self.depends_on = depends_on
        self.camera_id = camera_id
        self.class_names = class_names
        self.boxes_coordinates = boxes_coordinates
        self.objectness_scores = objectness_scores
        self.number_of_boxes = number_of_boxes
        self.image_resolution = image_resolution
        self.class_to_detect = class_to_detect
        self.detection_classes = detection_classes
        self.class_names_path = class_names_path
        self.objectness_threshold = objectness_threshold

    @classmethod
    def from_model_graph_node(
        cls,
        camera_id: str,
        model_id: str,
        model: Dict,
        inventory: Inventory,
        data_folder: Path,
    ):
        model_name = model["name"]
        class_names = inventory.models[model_name].get("class_names")
        class_to_detect = model.get("class_to_detect")
        class_names_path = inventory.models[model_name].get("class_names_path")
        objectness_threshold = inventory.models[model_name].get("objectness_threshold")

        if inventory.models[model_name].get("class_names_path") is not None:
            class_names_path = os.path.join(data_folder, class_names_path)
        try:
            boxes_coordinates = (
                inventory.models[model_name].get("output").get("boxes_coordinates")
            )
            objectness_scores = (
                inventory.models[model_name].get("output").get("objectness_scores")
            )
            number_of_boxes = (
                inventory.models[model_name].get("output").get("number_of_boxes")
            )
            detection_classes = (
                inventory.models[model_name].get("output").get("detection_classes")
            )
        except AttributeError:
            boxes_coordinates = None
            objectness_scores = None
            number_of_boxes = None
            detection_classes = None

        return ModelInfos(
            id=model_id,
            name=model_name,
            category=inventory.models[model_name]["category"],
            version=str(inventory.models[model_name]["version"]),
            depends_on=model["depends_on"],
            camera_id=camera_id,
            class_names=class_names,
            class_names_path=class_names_path,
            boxes_coordinates=boxes_coordinates,
            objectness_scores=objectness_scores,
            number_of_boxes=number_of_boxes,
            detection_classes=detection_classes,
            image_resolution=inventory.models[model_name].get("image_resolution"),
            class_to_detect=class_to_detect,
            objectness_threshold=objectness_threshold,
        )

    def __eq__(self, other) -> bool:
        return (
            other.name == self.name
            and other.category == self.category
            and other.version == self.version
            and other.depends_on == self.depends_on
            and other.camera_id == self.camera_id
            and other.class_names == self.class_names
            and other.class_names_path == self.class_names_path
            and other.boxes_coordinates == self.boxes_coordinates
            and other.objectness_scores == self.objectness_scores
            and other.number_of_boxes == self.number_of_boxes
            and other.detection_classes == self.detection_classes
            and other.image_resolution == self.image_resolution
            and other.class_to_detect == self.class_to_detect
            and other.objectness_threshold == self.objectness_threshold
        )

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class ModelTypes(Enum):
    CLASSIFICATION = "classification"
    OBJECT_DETECTION = "object_detection"
    OBJECT_DETECTION_WITH_CLASSIFICATION = "object_detection_with_classification"
    OBJECT_DETECTION_WITH_CLASSIFICATION_TORCH = (
        "object_detection_with_classification_torch"
    )
