from enum import Enum


class ModelType(str, Enum):
    classification = "classification"
    object_detection = "object_detection"
    segmentation = "segmentation"
