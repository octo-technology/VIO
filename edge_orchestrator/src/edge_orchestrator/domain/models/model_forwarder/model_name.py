from enum import Enum


class ModelName(str, Enum):
    fake_model = "fake_model"
    marker_quality_control = "marker_quality_control"
    pin_detection = "pin_detection"
    mobilenet_ssd_v2_coco = "mobilenet_ssd_v2_coco"
    mobilenet_ssd_v2_face = "mobilenet_ssd_v2_face"
    yolo_coco_nano = "yolo_coco_nano"
    duck_detection = "duck_detection"
