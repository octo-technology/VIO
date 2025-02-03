from enum import Enum


class ItemRuleType(str, Enum):
    MIN_THRESHOLD_RATIO_RULE = "min_threshold_ratio_rule"
    MIN_THRESHOLD_RULE = "min_threshold_rule"
