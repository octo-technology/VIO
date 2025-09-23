from enum import Enum


class PredictionType(str, Enum):
    CLASS_ = "class"
    OBJECTS = "objects"
    PROBABILITY = "probability"
    MASK = "mask"
