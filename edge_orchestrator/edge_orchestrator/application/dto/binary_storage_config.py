from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class BinaryStorageTypeEnum(str, Enum):
    azure_container = "azure_container"
    filesystem = "filesystem"
    gcp_bucket = "gcp_bucket"
    in_memory = "in_memory"


class BinaryStorageConfig(BaseModel):
    type: BinaryStorageTypeEnum = BinaryStorageTypeEnum.filesystem
    params: Optional[Dict[str, Any]] = None
