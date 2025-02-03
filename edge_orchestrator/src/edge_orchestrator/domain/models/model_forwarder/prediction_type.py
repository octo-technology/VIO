from enum import Enum


class PredictionType(str, Enum):
    class_ = "class"
    objects = "objects"
    probability = "probability"
    mask = "mask"
