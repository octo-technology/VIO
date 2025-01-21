from typing import Union

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType


class ItemRuleConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    item_rule_type: ItemRuleType
    threshold: Union[int, float]
