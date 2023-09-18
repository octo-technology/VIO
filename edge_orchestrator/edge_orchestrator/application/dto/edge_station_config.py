from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class ItemRuleNameEnum(str, Enum):
    min_threshold_KO_rule = "min_threshold_KO_rule"
    threshold_ratio_rule = "threshold_ratio_rule"


class ItemRule(BaseModel):
    name: ItemRuleNameEnum = ItemRuleNameEnum.min_threshold_KO_rule
    params: Optional[Dict[str, Any]] = None
