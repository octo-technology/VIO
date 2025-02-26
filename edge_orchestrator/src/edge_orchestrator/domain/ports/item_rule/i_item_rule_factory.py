from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule


class IItemRuleFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_item_rule(self, item_rule_config: ItemRuleConfig) -> IItemRule:
        pass
