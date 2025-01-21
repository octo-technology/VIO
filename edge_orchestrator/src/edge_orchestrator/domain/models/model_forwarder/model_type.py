from enum import Enum


class ModelType(str, Enum):
    FAKE = "fake"
    CLASSIFICATION = "classification"
    OBJECT_DETECTION = "object_detection"
    OBJECT_DETECTION_WITH_CLASSIFICATION = "object_detection_with_classification"
    SEGMENTATION = "segmentation"
