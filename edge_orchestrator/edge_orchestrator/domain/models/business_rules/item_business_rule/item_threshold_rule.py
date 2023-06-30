from typing import Dict

from edge_orchestrator.domain.models.business_rules.item_rule import ItemRule
from edge_orchestrator.domain.models.decision import Decision


class ThresholdRule(ItemRule):
    def __init__(self, threshold: int):
        self.threshold = threshold

    def get_item_decision(self, cameras_decisions: Dict[str, str]) -> Decision:
        ko_decisions = [
            decision
            for decision in cameras_decisions.values()
            if decision == Decision.KO.value
        ]

        if len(ko_decisions) >= self.threshold:
            return Decision.KO
        else:
            return Decision.OK
