from typing import Dict, Optional

from fastapi import UploadFile
from pydantic import ConfigDict, Field

from edge_orchestrator.application.models.item_base import ItemBase


class ItemIn(ItemBase):
    model_config = ConfigDict(use_enum_values=True)

    binaries: Optional[Dict[str, UploadFile]] = Field(default_factory=dict)
