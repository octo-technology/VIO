import logging

from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule


class UnexpectedLabelRule(ICameraRule):
    def __init__(self, camera_rule_config: CameraRuleConfig):
        self._camera_rule_config = camera_rule_config
        self._logger = logging.getLogger(__name__)
        self.unexpected_label: str = self._camera_rule_config.params["unexpected_label"]

    def _get_camera_decision(self, prediction: Prediction) -> Decision:
        classif = prediction
        if classif.prediction_type != ModelType.CLASSIFICATION:
            self._logger.warning(
                "You can not use an ExpectedLabelRule on something other than "
                f"{ModelType.CLASSIFICATION.value}, no decision returned."
            )
            return Decision.NO_DECISION

        if classif.label == self.unexpected_label:
            return Decision.KO
        else:
            return Decision.OK

    def apply_camera_rule(self, prediction: Prediction) -> Decision:
        return self._get_camera_decision(prediction)
