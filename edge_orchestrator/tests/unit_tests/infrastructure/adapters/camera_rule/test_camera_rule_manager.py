from uuid import UUID

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.camera_rule_factory import (
    CameraRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.camera_rule_manager import (
    CameraRuleManager,
)


class TestCameraRuleManager:

    def test_camera_rule_manager(
        self,
    ):
        # Given
        camera_rule_manager = CameraRuleManager(CameraRuleFactory())
        item = Item(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            cameras_metadata={
                "camera_#1": CameraConfig(
                    camera_id="camera_#1",
                    camera_type=CameraType.FAKE,
                    camera_rule_config=CameraRuleConfig(
                        camera_rule_type=CameraRuleType.EXPECTED_LABEL_RULE, expected_class="OK"
                    ),
                ),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2",
                    camera_type=CameraType.USB,
                    camera_rule_config=CameraRuleConfig(
                        camera_rule_type=CameraRuleType.UNEXPECTED_LABEL_RULE, unexpected_class="KO"
                    ),
                ),
                "camera_#3": CameraConfig(
                    camera_id="camera_#3",
                    camera_type=CameraType.RASPBERRY,
                    camera_rule_config=CameraRuleConfig(
                        camera_rule_type=CameraRuleType.MIN_NB_OBJECTS_RULE, class_to_detect="bike", threshold=1
                    ),
                ),
                "camera_#4": CameraConfig(
                    camera_id="camera_#4",
                    camera_type=CameraType.RASPBERRY,
                    camera_rule_config=CameraRuleConfig(
                        camera_rule_type=CameraRuleType.MAX_NB_OBJECTS_RULE, class_to_detect="moto", threshold=1
                    ),
                ),
            },
            predictions={
                "camera_#1": ClassifPrediction(prediction_type=PredictionType.class_, label="OK", probability=0.41),
                "camera_#2": ClassifPrediction(prediction_type=PredictionType.class_, label="KO", probability=0.96),
                "camera_#3": DetectionPrediction(
                    prediction_type=PredictionType.objects,
                    detected_objects={
                        "object_#1": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="bike"),
                        "object_#2": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
                    },
                ),
                "camera_#4": DetectionPrediction(
                    prediction_type=PredictionType.objects,
                    detected_objects={
                        "object_#1": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="bike"),
                        "object_#2": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
                        "object_#3": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
                    },
                ),
            },
            camera_decisions={},
        )

        # When
        camera_rule_manager.apply_camera_rules(item)

        # Then
        assert item.camera_decisions == {
            "camera_#1": Decision.OK,
            "camera_#2": Decision.KO,
            "camera_#3": Decision.OK,
            "camera_#4": Decision.KO,
        }
