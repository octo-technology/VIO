import logging
from typing import Dict

from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule
from edge_orchestrator.domain.ports.item_rule.i_item_rule_factory import (
    IItemRuleFactory,
)
from edge_orchestrator.domain.ports.item_rule.i_item_rule_manager import (
    IItemRuleManager,
)


class ItemRuleManager(IItemRuleManager):
    def __init__(self, item_rule_factory: IItemRuleFactory):
        self._item_rule_factory = item_rule_factory
        self._logger = logging.getLogger(__name__)
        self._item_rules: Dict[str, IItemRule] = {}

    def get_item_rule(self, item_rule_config: ItemRuleConfig) -> IItemRule:
        item_rule_type = item_rule_config.item_rule_type
        if item_rule_type not in self._item_rules or item_rule_config.recreate_me:
            self._item_rules[item_rule_type] = self._item_rule_factory.create_item_rule(item_rule_config)
        return self._item_rules[item_rule_type]
