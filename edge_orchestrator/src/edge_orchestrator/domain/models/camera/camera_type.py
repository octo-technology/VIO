from enum import Enum


class CameraType(str, Enum):
    FAKE = "fake"
    HTTP = "http"
