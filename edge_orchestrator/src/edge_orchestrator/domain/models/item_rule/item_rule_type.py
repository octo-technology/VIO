from enum import Enum


class ItemRuleType(str, Enum):
    MIN_THRESHOLD_OK_RATIO_RULE = "min_threshold_ok_ratio_rule"
    MIN_THRESHOLD_KO_RULE = "min_threshold_ko_rule"
