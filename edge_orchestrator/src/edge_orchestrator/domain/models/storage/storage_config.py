import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, model_validator

from edge_orchestrator.domain.models.storage.storage_type import StorageType


class StorageConfig(BaseModel):
    storage_type: StorageType = StorageType.FILESYSTEM
    bucket_name: Optional[str] = os.getenv("BUCKET_NAME", None)
    target_directory: Path = Path(os.getenv("EDGE_NAME", "data_storage"))

    @model_validator(mode="after")
    def check_params(self):
        if self.storage_type in [StorageType.GCP, StorageType.AWS, StorageType.AZURE]:
            if self.bucket_name is None:
                raise ValueError(f"storage_type {self.storage_type} should have bucket_name")
        return self
