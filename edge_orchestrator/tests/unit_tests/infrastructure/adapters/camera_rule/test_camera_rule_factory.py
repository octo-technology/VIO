from typing import Union

import pytest

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule
from edge_orchestrator.infrastructure.adapters.camera_rule.camera_rule_factory import (
    CameraRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.expected_label_rule import (
    ExpectedLabelRule,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.max_nb_objects_rule import (
    MaxNbObjectsRule,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.min_nb_objects_rule import (
    MinNbObjectsRule,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.unexpected_label_rule import (
    UnexpectedLabelRule,
)


class TestCameraRuleFactory:

    @pytest.mark.parametrize(
        "camera_rule_type,camera_rule_class,config_param",
        [
            (CameraRuleType.EXPECTED_LABEL_RULE, ExpectedLabelRule, "OK"),
            (CameraRuleType.UNEXPECTED_LABEL_RULE, UnexpectedLabelRule, "KO"),
            (CameraRuleType.MIN_NB_OBJECTS_RULE, MinNbObjectsRule, 1),
            (CameraRuleType.MAX_NB_OBJECTS_RULE, MaxNbObjectsRule, 2),
        ],
    )
    def test_should_return_the_specified_camera_rule_instance(
        self, camera_rule_type: CameraRuleType, camera_rule_class: ICameraRule, config_param: Union[str, int]
    ):
        # Given
        camera_rule_factory = CameraRuleFactory()
        if camera_rule_type == CameraRuleType.EXPECTED_LABEL_RULE:
            camera_rule_config = CameraRuleConfig(camera_rule_type=camera_rule_type, expected_class=config_param)
        elif camera_rule_type == CameraRuleType.UNEXPECTED_LABEL_RULE:
            camera_rule_config = CameraRuleConfig(camera_rule_type=camera_rule_type, unexpected_class=config_param)
        else:
            camera_rule_config = CameraRuleConfig(
                camera_rule_type=camera_rule_type, class_to_detect="OK", threshold=config_param
            )

        # When
        camera_rule = camera_rule_factory.create_camera_rule(camera_rule_config)

        # Then
        assert isinstance(camera_rule, camera_rule_class)
        assert hasattr(camera_rule, "apply_camera_rule")
        assert hasattr(camera_rule, "_get_camera_decision")
