from enum import Enum


class ImageExtension(str, Enum):
    BMP = "bmp"
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    TIFF = "tiff"
