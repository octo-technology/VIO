from typing import Union

from pydantic import BaseModel

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType


class ItemRuleConfig(BaseModel):
    item_rule_type: ItemRuleType
    expected_decision: Decision
    threshold: Union[int, float]
