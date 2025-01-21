import logging
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule import ItemRule
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.model_forwarder.decision import Decision


class MinThresholdOKRatioRule(ItemRule):
    def __init__(self, ItemRuleConfig: ItemRuleConfig):
        self._item_rule_config = ItemRuleConfig
        self._logger = logging.getLogger(__name__)

    def _get_item_decision(self, camera_decisions: Dict[str, Decision]) -> Decision:
        if len(camera_decisions) == 0:
            return Decision.NO_DECISION

        ok_decisions = [decision for decision in camera_decisions.values() if decision == Decision.OK]
        ratio_ok = len(ok_decisions) / len(camera_decisions)

        if ratio_ok >= self._item_rule_config.threshold:
            return Decision.OK
        else:
            return Decision.KO

    def apply_item_rules(self, item: Item):
        if len(item.camera_decisions) == 0:
            item.decision = Decision.NO_DECISION
        else:
            item.decision = self._get_item_decision(item.camera_decisions)
