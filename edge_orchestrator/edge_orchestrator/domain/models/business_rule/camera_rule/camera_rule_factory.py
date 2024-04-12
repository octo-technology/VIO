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
from edge_orchestrator.domain.models.business_rule.camera_rule.unexpected_label_rule import (
    UnexpectedLabelRule,
)

AVAILABLE_CAMERA_RULES = {
    "expected_label_rule": ExpectedLabelRule,
    "min_nb_objects_rule": MinNbObjectsRule,
    "max_nb_objects_rule": MaxNbObjectsRule,
    "unexpected_label_rule": UnexpectedLabelRule,
}


def get_camera_rule(rule_name: str, **camera_rule_parameters) -> CameraRule:
    try:
        camera_rule = AVAILABLE_CAMERA_RULES[rule_name]
        return camera_rule(**camera_rule_parameters)
    except KeyError as error:
        raise NotImplementedError(f"Unknown camera rule name: {rule_name}") from error
