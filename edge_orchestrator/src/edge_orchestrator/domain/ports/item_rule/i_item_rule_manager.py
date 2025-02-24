from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule
from edge_orchestrator.domain.ports.item_rule.i_item_rule_factory import (
    IItemRuleFactory,
)


class IItemRuleManager(ABC):
    _item_rule_factory: IItemRuleFactory
    _logger: Logger
    _item_rules: Dict[str, IItemRule]

    @abstractmethod
    def get_item_rule(self, item_rule_config: ItemRuleConfig) -> IItemRule:
        pass
