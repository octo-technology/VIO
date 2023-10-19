from typing import Type

from edge_orchestrator.domain.models.business_rule.item_rule.item_rule import (
    ItemRule,
)
from edge_orchestrator.domain.models.business_rule.item_rule.min_threshold_ko_rule import (
    MinThresholdKORule,
)
from edge_orchestrator.domain.models.business_rule.item_rule.min_threshold_ok_ratio_rule import (
    MinThresholdOKRatioRule,
)

AVAILABLE_ITEM_RULES = {
    "min_threshold_ok_ratio_rule": MinThresholdOKRatioRule,
    "min_threshold_ko_rule": MinThresholdKORule,
}


def get_item_rule(rule_name: str) -> Type[ItemRule]:
    try:
        return AVAILABLE_ITEM_RULES[rule_name]
    except KeyError as error:
        raise NotImplementedError(f"Unknown item rule name: {rule_name}") from error
