import logging

from edge_orchestrator.domain.models.item_rule.item_rule import ItemRule
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.ports.item_rule.i_item_rule_factory import (
    IItemRuleFactory,
)


class ItemRuleFactory(IItemRuleFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_item_rule(self, item_rule_config: ItemRuleConfig) -> ItemRule:
        if item_rule_config.item_rule_type == ItemRuleType.MIN_THRESHOLD_KO_RULE.value:
            from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_ko_rule import (
                MinThresholdKORule,
            )

            return MinThresholdKORule(item_rule_config)

        elif item_rule_config.item_rule_type == ItemRuleType.MIN_THRESHOLD_OK_RATIO_RULE.value:
            from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_ok_ratio_rule import (
                MinThresholdOKRatioRule,
            )

            return MinThresholdOKRatioRule(item_rule_config)

        else:
            raise ValueError(f"Item rule type {item_rule_config.item_rule_type} is not supported")
