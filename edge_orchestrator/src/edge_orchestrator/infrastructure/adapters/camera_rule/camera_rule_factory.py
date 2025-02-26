import logging

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_factory import (
    ICameraRuleFactory,
)


class CameraRuleFactory(ICameraRuleFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_camera_rule(self, camera_rule_config: CameraRuleConfig) -> ICameraRule:
        camera_rule_type = camera_rule_config.camera_rule_type
        if camera_rule_type == CameraRuleType.EXPECTED_LABEL_RULE:
            from edge_orchestrator.infrastructure.adapters.camera_rule.expected_label_rule import (
                ExpectedLabelRule,
            )

            return ExpectedLabelRule(camera_rule_config)

        elif camera_rule_type == CameraRuleType.UNEXPECTED_LABEL_RULE:
            from edge_orchestrator.infrastructure.adapters.camera_rule.unexpected_label_rule import (
                UnexpectedLabelRule,
            )

            return UnexpectedLabelRule(camera_rule_config)

        elif camera_rule_type == CameraRuleType.MAX_NB_OBJECTS_RULE:
            from edge_orchestrator.infrastructure.adapters.camera_rule.max_nb_objects_rule import (
                MaxNbObjectsRule,
            )

            return MaxNbObjectsRule(camera_rule_config)

        elif camera_rule_type == CameraRuleType.MIN_NB_OBJECTS_RULE:
            from edge_orchestrator.infrastructure.adapters.camera_rule.min_nb_objects_rule import (
                MinNbObjectsRule,
            )

            return MinNbObjectsRule(camera_rule_config)

        else:
            raise ValueError(f"Camera rule type {camera_rule_config.camera_rule_type} is not supported")
