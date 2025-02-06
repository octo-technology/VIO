import logging

from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule
from edge_orchestrator.domain.ports.item_rule.i_item_rule_factory import (
    IItemRuleFactory,
)


class ItemRuleFactory(IItemRuleFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_item_rule(self, item_rule_config: ItemRuleConfig) -> IItemRule:
        if item_rule_config.item_rule_type == ItemRuleType.MIN_THRESHOLD_RULE.value:
            from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_rule import (
                MinThresholdRule,
            )

            return MinThresholdRule(item_rule_config)

        elif item_rule_config.item_rule_type == ItemRuleType.MIN_THRESHOLD_RATIO_RULE.value:
            from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_ratio_rule import (
                MinThresholdRatioRule,
            )

            return MinThresholdRatioRule(item_rule_config)

        else:
            raise ValueError(f"Item rule type {item_rule_config.item_rule_type} is not supported")
