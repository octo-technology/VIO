from typing import Dict, Optional

from fastapi import UploadFile
from pydantic import Field

from edge_orchestrator.interface.api.models.item_base import ItemBase


class ItemIn(ItemBase):
    binaries: Optional[Dict[str, UploadFile]] = Field(default_factory=dict)
