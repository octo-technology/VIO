from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.item_rule.item_rule import ItemRule
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig


class IItemRuleFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_item_rule(self, item_rule_config: ItemRuleConfig) -> ItemRule:
        pass
