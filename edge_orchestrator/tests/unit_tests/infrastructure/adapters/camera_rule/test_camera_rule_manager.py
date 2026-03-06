from uuid import UUID

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.camera_rule.camera_rule_type import CameraRuleType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.models.pipeline_step import PipelineStep
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
        pipeline_steps = {
            "step_1": PipelineStep(
                camera_id="camera_#1",
                model_forwarder_config=ModelForwarderConfig(model_name="fake_model", model_version="1"),
                camera_rule_config=CameraRuleConfig(
                    camera_rule_type=CameraRuleType.EXPECTED_LABEL_RULE, expected_class="OK"
                ),
            ),
            "step_2": PipelineStep(
                camera_id="camera_#2",
                model_forwarder_config=ModelForwarderConfig(model_name="fake_model", model_version="1"),
                camera_rule_config=CameraRuleConfig(
                    camera_rule_type=CameraRuleType.UNEXPECTED_LABEL_RULE, unexpected_class="KO"
                ),
            ),
            "step_3": PipelineStep(
                camera_id="camera_#3",
                model_forwarder_config=ModelForwarderConfig(model_name="fake_model", model_version="1"),
                camera_rule_config=CameraRuleConfig(
                    camera_rule_type=CameraRuleType.MIN_NB_OBJECTS_RULE, class_to_detect="bike", threshold=1
                ),
            ),
            "step_4": PipelineStep(
                camera_id="camera_#4",
                model_forwarder_config=ModelForwarderConfig(model_name="fake_model", model_version="1"),
                camera_rule_config=CameraRuleConfig(
                    camera_rule_type=CameraRuleType.MAX_NB_OBJECTS_RULE, class_to_detect="moto", threshold=1
                ),
            ),
        }
        item = Item(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            predictions={
                "step_1": ClassifPrediction(prediction_type=PredictionType.class_, label="OK", probability=0.41),
                "step_2": ClassifPrediction(prediction_type=PredictionType.class_, label="KO", probability=0.96),
                "step_3": DetectionPrediction(
                    prediction_type=PredictionType.objects,
                    detected_objects={
                        "object_#1": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="bike"),
                        "object_#2": DetectedObject(location=[1, 2, 3, 4], objectness=0.6578, label="moto"),
                    },
                ),
                "step_4": DetectionPrediction(
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
        camera_rule_manager.apply_camera_rules(item, pipeline_steps)

        # Then
        assert item.camera_decisions == {
            "step_1": Decision.OK,
            "step_2": Decision.KO,
            "step_3": Decision.OK,
            "step_4": Decision.KO,
        }
