import pytest
from pydantic import ValidationError

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType


class TestCameraRuleConfig:

    @pytest.mark.parametrize(
        "camera_rule_type",
        [
            CameraRuleType.EXPECTED_LABEL_RULE,
            CameraRuleType.UNEXPECTED_LABEL_RULE,
            CameraRuleType.MIN_NB_OBJECTS_RULE,
            CameraRuleType.MAX_NB_OBJECTS_RULE,
        ],
    )
    def test_camera_rule_should_raise_exception_without_required_parameters(self, camera_rule_type: CameraRuleType):
        # Given / When
        with pytest.raises(ValidationError) as e:
            CameraRuleConfig(camera_rule_type=camera_rule_type)

        # Then
        assert (
            "Either expected_class or unexpected_class or (class_to_detect and threshold) is required (exclusive)"
            in str(e.value)
        )

    @pytest.mark.parametrize(
        "camera_rule_type",
        [
            CameraRuleType.EXPECTED_LABEL_RULE,
            CameraRuleType.UNEXPECTED_LABEL_RULE,
        ],
    )
    def test_camera_rule_should_raise_exception_with_bad_params(self, camera_rule_type: CameraRuleType):
        # Given / When
        with pytest.raises(ValidationError) as e:
            if camera_rule_type == CameraRuleType.EXPECTED_LABEL_RULE:
                CameraRuleConfig(camera_rule_type=camera_rule_type, expected_class="OK", threshold=2)
            elif camera_rule_type == CameraRuleType.UNEXPECTED_LABEL_RULE:
                CameraRuleConfig(camera_rule_type=camera_rule_type, unexpected_class="OK", class_to_detect="KO")

        # Then
        assert (
            "Either expected_class or unexpected_class or (class_to_detect and threshold) is required (exclusive)"
            in str(e.value)
        )

    @pytest.mark.parametrize(
        "camera_rule_type",
        [
            CameraRuleType.EXPECTED_LABEL_RULE,
            CameraRuleType.UNEXPECTED_LABEL_RULE,
        ],
    )
    def test_camera_rule_should_raise_exception_with_bad_arguments(self, camera_rule_type: CameraRuleType):
        # Given / When
        with pytest.raises(ValidationError) as e:
            if camera_rule_type == CameraRuleType.EXPECTED_LABEL_RULE:
                CameraRuleConfig(camera_rule_type=camera_rule_type, unexpected_class="OK")
            elif camera_rule_type == CameraRuleType.UNEXPECTED_LABEL_RULE:
                CameraRuleConfig(camera_rule_type=camera_rule_type, expected_class="OK")

        # Then
        assert (
            "Either provide (EXPECTED_LABEL_RULE and expected_class) or (UNEXPECTED_LABEL_RULE and unexpected_class)"
            in str(e.value)
        )
