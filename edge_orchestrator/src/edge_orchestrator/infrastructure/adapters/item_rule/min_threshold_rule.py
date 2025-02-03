import logging
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule import ItemRule
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.model_forwarder.decision import Decision


class MinThresholdRule(ItemRule):
    def __init__(self, ItemRuleConfig: ItemRuleConfig):
        self._item_rule_config = ItemRuleConfig
        self._logger = logging.getLogger(__name__)

    def _get_item_decision(self, camera_decisions: Dict[str, Decision]) -> Decision:
        expected_decisions = [
            decision for decision in camera_decisions.values() if decision == self._item_rule_config.expected_decision
        ]

        if len(camera_decisions) == 0:
            return Decision.NO_DECISION
        elif len(expected_decisions) >= self._item_rule_config.threshold:
            return Decision.OK
        else:
            return Decision.KO

    def apply_item_rules(self, item: Item):
        if len(item.camera_decisions) == 0:
            item.decision = Decision.NO_DECISION
        else:
            item.decision = self._get_item_decision(item.camera_decisions)
