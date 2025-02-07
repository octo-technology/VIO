from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    creation_date: datetime = Field(default_factory=datetime.now)
