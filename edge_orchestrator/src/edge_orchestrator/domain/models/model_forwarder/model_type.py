from enum import Enum


class ModelType(str, Enum):
    FAKE = "fake"
    classification = "classification"
    object_detection = "object_detection"
    segmentation = "segmentation"
