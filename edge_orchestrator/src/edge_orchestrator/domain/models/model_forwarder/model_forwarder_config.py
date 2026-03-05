from typing import Optional

from pydantic import BaseModel, computed_field
from pydantic_core import Url

from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType


class ModelForwarderConfig(BaseModel):
    model_name: str
    model_version: Optional[str] = "1"
    model_serving_url: Optional[Url] = None
    # Optional field kept for FakeModelForwarder only
    model_type: Optional[ModelType] = None

    @computed_field
    @property
    def model_id(self) -> str:
        return f"{self.model_name}_{self.model_version}"
