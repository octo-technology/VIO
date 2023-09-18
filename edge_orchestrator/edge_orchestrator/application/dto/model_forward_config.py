from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class ModelForwardTypeEnum(str, Enum):
    fake = "fake"
    tf_serving = "tf_serving"


class ModelForwardConfig(BaseModel):
    type: ModelForwardTypeEnum
    params: Optional[Dict[str, Any]] = None
