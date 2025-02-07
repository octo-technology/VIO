from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic_core import Url

from edge_orchestrator.domain.models.model_forwarder.image_resolution import (
    ImageResolution,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType

# Version = Annotated[
#     str,
#     StringConstraints(pattern=r"^(0|[1-9]\d{0,2})\.(0|[1-9]\d{0,2})\.(0|[1-9]\d{0,2})$"),
# ]


class ModelForwarderConfig(BaseModel):
    model_name: ModelName
    model_type: ModelType
    expected_image_resolution: ImageResolution
    # model_version: Optional[Version] = None
    model_version: str
    class_names: Optional[List[str]] = Field(default_factory=list)
    class_names_filepath: Optional[Path] = None
    model_serving_url: Optional[Url] = None
    recreate_me: Optional[bool] = False

    @computed_field
    @property
    def model_id(self) -> str:
        return f"{self.model_name.value}_{self.model_type.value}_{self.model_version}"

    @model_validator(mode="after")
    def check_class_names_or_class_names_path(self):
        if self.model_type in [ModelType.classification, ModelType.object_detection] and (
            (not self.class_names and not self.class_names_filepath) or (self.class_names and self.class_names_filepath)
        ):
            raise ValueError("Either class_names or class_names_path is required (exclusive)")
        return self
