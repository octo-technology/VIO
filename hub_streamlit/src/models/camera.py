from typing import List, Optional

from pydantic import BaseModel


class Camera(BaseModel):
    id: str
    pictures: List[dict] = []
