from typing import Optional

from pydantic import BaseModel, PositiveInt, model_validator

from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType


# TODO: add more validation, ie: if camera_rule_type == MIN_NB_OBJECTS_RULE and expected_class provided
class CameraRuleConfig(BaseModel):
    camera_rule_type: CameraRuleType
    expected_class: Optional[str] = None
    unexpected_class: Optional[str] = None
    class_to_detect: Optional[str] = None
    threshold: Optional[PositiveInt] = None

    @model_validator(mode="after")
    def check_params(self):
        if all([self.expected_class, self.unexpected_class, (self.class_to_detect and self.threshold)]) or all(
            [not self.expected_class, not self.unexpected_class, not (self.class_to_detect and self.threshold)]
        ):
            raise ValueError(
                "Either expected_class or unexpected_class or (class_to_detect and threshold) is required (exclusive)"
            )
        if (self.expected_class or self.unexpected_class) and (self.threshold or self.class_to_detect):
            raise ValueError(
                "Either expected_class or unexpected_class or (class_to_detect and threshold) is required (exclusive)"
            )
        if (self.camera_rule_type is CameraRuleType.EXPECTED_LABEL_RULE and self.unexpected_class) or (
            self.camera_rule_type is CameraRuleType.UNEXPECTED_LABEL_RULE and self.expected_class
        ):
            raise ValueError(
                "Either provide (EXPECTED_LABEL_RULE and expected_class) or "
                "(UNEXPECTED_LABEL_RULE and unexpected_class)"
            )
        return self
