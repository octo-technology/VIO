from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[UUID] = Field(default_factory=uuid4)
