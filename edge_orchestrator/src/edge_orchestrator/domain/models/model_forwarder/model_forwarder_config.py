from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic_core import Url

from edge_orchestrator.domain.models.model_forwarder.image_resolution import (
    ImageResolution,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType


class ModelForwarderConfig(BaseModel):
    model_name: Union[str, ModelName]
    model_type: ModelType
    expected_image_resolution: ImageResolution
    model_version: Optional[str] = "1"
    class_names: Optional[List[str]] = Field(default_factory=list)
    class_names_filepath: Optional[Path] = None
    model_serving_url: Optional[Url] = None

    @computed_field
    @property
    def model_id(self) -> str:
        return f"{self.model_name}_{self.model_type.value}_{self.model_version}"

    @model_validator(mode="after")
    def convert_model_name_to_str(self):
        if isinstance(self.model_name, ModelName):
            self.model_name = self.model_name.value
        return self

    @model_validator(mode="after")
    def check_class_names_path(self):
        if self.class_names_filepath and not self.class_names_filepath.exists():
            raise ValueError(f"Class names file {self.class_names_filepath} does not exist")
        return self

    @model_validator(mode="after")
    def check_class_names_or_class_names_path(self):
        if self.model_type in [ModelType.classification, ModelType.object_detection] and (
            (not self.class_names and not self.class_names_filepath) or (self.class_names and self.class_names_filepath)
        ):
            raise ValueError("Either class_names or class_names_path is required (exclusive)")
        return self
