from enum import Enum


class ModelName(str, Enum):
    FAKE_MODEL = "fake_model"
    MARKER_QUALITY_CONTROL = "marker_quality_control"
    PIN_DETECTION = "pin_detection"
    MOBILENET_SSD_V2_COCO = "mobilenet_ssd_v2_coco"
    MOBILENET_SSD_V2_FACE = "mobilenet_ssd_v2_face"
    YOLO_COCO_NANO = "yolo_coco_nano"
