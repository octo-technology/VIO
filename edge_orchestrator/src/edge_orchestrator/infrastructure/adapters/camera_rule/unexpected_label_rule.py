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


class UnexpectedLabelRule(ICameraRule):
    def __init__(self, camera_rule_config: CameraRuleConfig):
        self._camera_rule_config = camera_rule_config
        self._logger = logging.getLogger(__name__)

    def _get_camera_decision(self, prediction: Prediction) -> Decision:
        classif = prediction
        if classif.prediction_type != PredictionType.class_:
            self._logger.warning(
                "You can not use an ExpectedLabelRule on something other than "
                f"{PredictionType.class_.value}, no decision returned."
            )
            return Decision.NO_DECISION
        if classif.label is None:
            return Decision.NO_DECISION

        if classif.label == self._camera_rule_config.unexpected_class:
            return Decision.KO
        else:
            return Decision.OK

    def apply_camera_rule(self, prediction: Prediction) -> Decision:
        return self._get_camera_decision(prediction)
