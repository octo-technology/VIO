from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule


class ICameraRuleFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_camera_rule(self, camera_rule_config: CameraRuleConfig) -> ICameraRule:
        pass
