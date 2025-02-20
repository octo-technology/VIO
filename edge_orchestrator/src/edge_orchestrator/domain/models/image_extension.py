from enum import Enum


class ImageExtension(str, Enum):
    bmp = "bmp"
    jpeg = "jpeg"
    jpg = "jpg"
    png = "png"
    tiff = "tiff"
