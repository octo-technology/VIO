from typing import List, Optional

from pydantic import BaseModel


class Camera(BaseModel):
    pictures: Optional[List[dict]] = []
