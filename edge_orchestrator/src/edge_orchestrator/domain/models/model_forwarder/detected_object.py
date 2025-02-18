from typing import List, Optional

from pydantic import BaseModel, Field


class DetectedObject(BaseModel):
    location: List[float] = Field(..., min_length=4, max_length=4)
    objectness: float
    label: Optional[str] = None
