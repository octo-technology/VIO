from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_factory import (
    ICameraRuleFactory,
)


class ICameraRuleManager(ABC):
    _camera_rule_factory: ICameraRuleFactory
    _logger: Logger
    _camera_rules: Dict[str, ICameraRule]

    @abstractmethod
    def _get_camera_rule(self, camera_rule_config: CameraRuleConfig) -> ICameraRule:
        pass

    @abstractmethod
    def apply_camera_rules(self, item: Item):
        pass
