import logging

from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule


class MaxNbObjectsRule(ICameraRule):
    def __init__(self, camera_rule_config: CameraRuleConfig):
        self._camera_rule_config = camera_rule_config
        self._logger = logging.getLogger(__name__)
        self.class_to_detect: str = self._camera_rule_config.params["class_to_detect"]
        self.max_threshold: int = self._camera_rule_config.params["max_threshold"]

    def _get_camera_decision(self, prediction: Prediction) -> Decision:
        detec_predict_with_classif = prediction
        if detec_predict_with_classif.prediction_type != ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION:
            self._logger.warning(
                "You can not use an MaxNbObjectsRule on something other than "
                f"{ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION.value}, no decision returned."
            )
            return Decision.NO_DECISION

        detected_objects = detec_predict_with_classif.detected_objects
        objects_of_interest = [
            detected_object for detected_object in detected_objects if detected_object.label == self.class_to_detect
        ]

        if len(detected_objects) == 0:
            camera_decision = Decision.NO_DECISION
        elif len(objects_of_interest) < self.max_threshold:
            camera_decision = Decision.KO
        else:
            camera_decision = Decision.OK

        return camera_decision

    def apply_camera_rule(self, prediction: Prediction) -> Decision:
        return self._get_camera_decision(prediction)
