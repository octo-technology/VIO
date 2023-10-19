from typing import Dict

from domain.models.business_rule.item_rule.item_rule import ItemRule
from edge_orchestrator.domain.models.decision import Decision


class MinThresholdOKRatioRule(ItemRule):
    def __init__(self, min_threshold: float):
        self.min_threshold = min_threshold

    def get_item_decision(self, cameras_decisions: Dict[str, str]) -> Decision:
        ok_decisions = [
            decision
            for decision in cameras_decisions.values()
            if decision == Decision.OK.value
        ]

        ratio_ok = len(ok_decisions) / len(cameras_decisions)

        if ratio_ok >= self.min_threshold:
            return Decision.OK
        else:
            return Decision.KO
