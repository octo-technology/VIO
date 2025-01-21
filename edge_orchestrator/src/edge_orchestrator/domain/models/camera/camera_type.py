from enum import Enum


class CameraType(str, Enum):
    FAKE = "fake"
    USB = "usb"
    RASPBERRY = "raspberry"
