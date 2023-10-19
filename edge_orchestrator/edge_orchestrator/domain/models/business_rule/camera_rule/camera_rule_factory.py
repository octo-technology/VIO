from typing import Type

from edge_orchestrator.domain.models.business_rule.camera_rule.camera_rule import (
    CameraRule,
)
from edge_orchestrator.domain.models.business_rule.camera_rule.expected_label_rule import (
    ExpectedLabelRule,
)
from edge_orchestrator.domain.models.business_rule.camera_rule.max_nb_objects_rule import (
    MaxNbObjectsRule,
)
from edge_orchestrator.domain.models.business_rule.camera_rule.min_nb_objects_rule import (
    MinNbObjectsRule,
)

AVAILABLE_CAMERA_RULES = {
    "expected_label_rule": ExpectedLabelRule,
    "min_nb_objects_rule": MinNbObjectsRule,
    "max_nb_objects_rule": MaxNbObjectsRule,
}


def get_camera_rule(rule_name: str) -> Type[CameraRule]:
    try:
        return AVAILABLE_CAMERA_RULES[rule_name]
    except KeyError as error:
        raise NotImplementedError(f"Unknown camera rule name: {rule_name}") from error
