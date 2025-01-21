from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.model_forwarder.decision import Decision


class ItemRule(ABC):
    _item_rule_config: ItemRuleConfig
    _logger: Logger

    @abstractmethod
    def _get_item_decision(self, camera_decisions: Dict[str, Decision]) -> Decision:
        pass

    @abstractmethod
    def apply_item_rules(self, item: Item):
        pass
