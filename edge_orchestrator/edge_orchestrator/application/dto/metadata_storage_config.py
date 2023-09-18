from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class MetadataStorageTypeEnum(str, Enum):
    azure_container = "azure_container"
    filesystem = "filesystem"
    gcp_bucket = "gcp_bucket"
    in_memory = "in_memory"
    mongo_db = "mongo_db"


class MetadataStorageConfig(BaseModel):
    type: MetadataStorageTypeEnum = MetadataStorageTypeEnum.filesystem
    params: Optional[Dict[str, Any]] = None
