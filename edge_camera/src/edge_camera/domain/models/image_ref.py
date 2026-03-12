from datetime import datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field


class ImageRef(BaseModel):
    uri: str
    camera_id: str
    captured_at: datetime = Field(default_factory=datetime.now)
    size_bytes: int

    @classmethod
    def from_path(cls, path: Path, camera_id: str) -> "ImageRef":
        return cls(
            uri=path.as_uri(),
            camera_id=camera_id,
            size_bytes=path.stat().st_size,
        )
