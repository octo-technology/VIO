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
from edge_orchestrator.infrastructure.adapters.camera_rule.max_nb_objects_rule import (
    MaxNbObjectsRule,
)


class TestMaxNbObjectsRule:

    def test_max_nb_objects_rule(self):
        # Given
        max_nb_objects_rule = MaxNbObjectsRule(
            camera_rule_config=CameraRuleConfig(
                camera_rule_type=CameraRuleType.MAX_NB_OBJECTS_RULE, class_to_detect="bike", threshold=1
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
        actual_decision = max_nb_objects_rule.apply_camera_rule(prediction)

        # Then
        assert actual_decision == Decision.OK
