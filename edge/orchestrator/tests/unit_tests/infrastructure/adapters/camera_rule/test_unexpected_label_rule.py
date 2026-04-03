from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.unexpected_label_rule import (
    UnexpectedLabelRule,
)


class TestUnexpectedLabelRule:

    def test_unexpected_label_rule(self):
        # Given
        unexpected_label_rule = UnexpectedLabelRule(
            camera_rule_config=CameraRuleConfig(
                camera_rule_type=CameraRuleType.UNEXPECTED_LABEL_RULE, unexpected_class="bike"
            )
        )
        prediction = ClassifPrediction(prediction_type=PredictionType.class_, label="people", probability=0.2354)

        # When
        actual_decision = unexpected_label_rule.apply_camera_rule(prediction)

        # Then
        assert actual_decision == Decision.OK
