import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from edge_orchestrator.domain.models.storage.storage_type import StorageType


class StorageConfig(BaseModel):
    storage_type: StorageType = StorageType.FILESYSTEM
    target_directory: Path = Path(os.getenv("BUCKET_NAME", "data_storage"))
    prefix: Optional[str] = os.getenv("EDGE_NAME", None)
    recreate_me: Optional[bool] = False
