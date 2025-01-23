from typing import List, Optional

from pydantic import BaseModel
from PIL import Image


class Camera(BaseModel):
    id: str
    pictures: List[dict] = []

    def add_picture(
        self,
        picture: Image,
    ):
        self.pictures.append(picture)
