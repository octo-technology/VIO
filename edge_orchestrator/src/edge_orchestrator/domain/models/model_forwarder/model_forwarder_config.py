from pathlib import Path
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic_core import Url

from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType

Version = Annotated[
    str,
    StringConstraints(pattern=r"^(0|[1-9]\d{0,2})\.(0|[1-9]\d{0,2})\.(0|[1-9]\d{0,2})$"),
]


class ModelForwarderConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    model_id: str
    model_type: ModelType
    model_version: Optional[Version] = None
    class_names: Optional[List[str]] = Field(default_factory=list)
    class_names_filepath: Optional[Path] = None
    model_serving_url: Optional[Url] = None
