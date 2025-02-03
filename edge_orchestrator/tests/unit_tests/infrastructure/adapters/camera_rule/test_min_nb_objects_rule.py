from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.min_nb_objects_rule import (
    MinNbObjectsRule,
)


class TestMinNbObjectsRule:

    def test_min_nb_objects_rule(self):
        # Given
        min_nb_objects_rule = MinNbObjectsRule(
            camera_rule_config=CameraRuleConfig(
                camera_rule_type=CameraRuleType.MIN_NB_OBJECTS_RULE, class_to_detect="bike", threshold=1
            )
        )
        prediction = DetectionPrediction(
            prediction_type=PredictionType.objects,
            detected_objects={
                "object_#1": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="bike"),
                "object_#2": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
                "object_#3": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
            },
        )

        # When
        actual_decision = min_nb_objects_rule.apply_camera_rule(prediction)

        # Then
        assert actual_decision == Decision.OK
