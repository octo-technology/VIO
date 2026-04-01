from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class InspectionEventStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class InspectionEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    item_id: UUID = Field(default_factory=uuid4)
    station_name: str
    status: InspectionEventStatus = InspectionEventStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    retry_count: int = 0
    error: Optional[str] = None
