from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class TelemetrySinkTypeEnum(str, Enum):
    azure_iot_hub = "azure_iot_hub"
    fake = "fake"
    postgres = "postgres"


class TelemetrySinkDto(BaseModel):
    type: TelemetrySinkTypeEnum = TelemetrySinkTypeEnum.fake
    params: Optional[Dict[str, Any]] = None
