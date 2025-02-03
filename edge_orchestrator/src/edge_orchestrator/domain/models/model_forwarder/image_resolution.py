from pydantic import BaseModel, PositiveInt


class ImageResolution(BaseModel):
    width: PositiveInt
    height: PositiveInt
