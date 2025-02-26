from typing import Dict, List

from fastapi import UploadFile
from pydantic import Field

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.interface.api.models.item_base import ItemBase


class ItemIn(ItemBase):
    binaries: List[UploadFile] = Field(default_factory=list)
    cameras_metadata: Dict[str, CameraConfig] = Field(default_factory=dict)
