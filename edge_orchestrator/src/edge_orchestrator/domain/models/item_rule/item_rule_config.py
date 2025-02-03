from typing import Union

from pydantic import BaseModel

from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.model_forwarder.decision import Decision


class ItemRuleConfig(BaseModel):
    item_rule_type: ItemRuleType
    expected_decision: Decision
    threshold: Union[int, float]
