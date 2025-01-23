from typing import List

from PIL import Image
from pydantic import BaseModel


class Camera(BaseModel):
    id: str
    pictures: List[dict] = []

    def add_picture(
        self,
        picture: Image,
    ):
        self.pictures.append(picture)
