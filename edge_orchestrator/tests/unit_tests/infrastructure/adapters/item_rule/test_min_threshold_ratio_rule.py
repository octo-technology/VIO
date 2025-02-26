from uuid import UUID

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_ratio_rule import (
    MinThresholdRatioRule,
)


class TestMinThresholdRatioRule:

    def test_min_threshold_ratio_rule(
        self,
    ):
        # Given
        item_rule = MinThresholdRatioRule(
            ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RATIO_RULE, expected_decision=Decision.OK, threshold=0.6
            )
        )
        item = Item(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            camera_decisions={
                "camera_#1": Decision.OK,
                "camera_#2": Decision.KO,
                "camera_#3": Decision.OK,
                "camera_#4": Decision.KO,
            },
        )

        # When
        item_rule.apply_item_rules(item)

        # Then
        assert item.decision == Decision.KO
