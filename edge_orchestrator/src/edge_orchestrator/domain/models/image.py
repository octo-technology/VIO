from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Image(BaseModel):
    creation_date: datetime = Field(default_factory=datetime.now)
    storing_path: Optional[Path] = None
    image_bytes: bytes = Field(exclude=True, default=None)
