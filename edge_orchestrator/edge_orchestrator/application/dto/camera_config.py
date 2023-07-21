from enum import Enum
from typing import Dict, Any, List

from pydantic import (
    BaseModel,
    StringConstraints, PositiveInt,
)
from typing_extensions import Annotated

from edge_orchestrator.application.dto.model_config import ModelConfig

CameraName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, pattern=r"camera_#[0-9]+"
    ),
]


class CameraTypeEnum(str, Enum):
    fake = "fake"
    pi_camera = "pi_camera"
    usb_camera = "usb_camera"


class CameraPositionEnum(str, Enum):
    front = "front"
    back = "back"
    left = "left"
    right = "right"


class CameraRuleNameEnum(str, Enum):
    expected_label_rule = "expected_label_rule"
    max_nb_objects_rule = "max_nb_objects_rule"
    min_nb_objects_rule = "min_nb_objects_rule"


class CameraRule(BaseModel):
    name: CameraRuleNameEnum = CameraRuleNameEnum.expected_label_rule
    params: Dict[str, Any] = None


class CameraConfig(BaseModel):
    name: CameraName = "camera_#1"
    type: CameraTypeEnum = CameraTypeEnum.fake
    source: str
    position: CameraPositionEnum = CameraPositionEnum.front
    exposition: PositiveInt = 100


class CameraLogic(BaseModel):
    name: CameraName = "camera_#1"
    models_graph: List[ModelConfig]
    rule: CameraRule = CameraRule()
