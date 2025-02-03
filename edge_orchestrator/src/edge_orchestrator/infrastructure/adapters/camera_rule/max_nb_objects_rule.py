import logging

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule


class MaxNbObjectsRule(ICameraRule):
    def __init__(self, camera_rule_config: CameraRuleConfig):
        self._camera_rule_config = camera_rule_config
        self._logger = logging.getLogger(__name__)

    def _get_camera_decision(self, prediction: Prediction) -> Decision:
        detec_predict_with_classif = prediction
        if detec_predict_with_classif.prediction_type != PredictionType.objects:
            self._logger.warning(
                "You can not use an MaxNbObjectsRule on something other than "
                f"{PredictionType.objects.value}, no decision returned."
            )
            return Decision.NO_DECISION

        detected_objects = detec_predict_with_classif.detected_objects

        if len(detected_objects) == 0:
            return Decision.NO_DECISION

        objects_of_interest = [
            detected_object
            for detected_object in detected_objects.values()
            if detected_object.label == self._camera_rule_config.class_to_detect
        ]

        if len(objects_of_interest) > self._camera_rule_config.threshold:
            return Decision.KO
        else:
            return Decision.OK

    def apply_camera_rule(self, prediction: Prediction) -> Decision:
        return self._get_camera_decision(prediction)
