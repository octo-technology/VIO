from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction


class ICameraRule(ABC):
    _logger: Logger
    _camera_rule_config: CameraRuleConfig

    @abstractmethod
    def _get_camera_decision(self, prediction: Prediction) -> Decision:
        pass

    @abstractmethod
    def apply_camera_rule(self, item: Item):
        pass
