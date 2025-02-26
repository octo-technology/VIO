from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_factory import (
    ItemRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_manager import (
    ItemRuleManager,
)


class TestItemRuleManager:

    def test_camera_rule_manager(
        self,
    ):
        # Given
        item_rule_manager = ItemRuleManager(ItemRuleFactory())
        item_rule_config = ItemRuleConfig(
            item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.KO, threshold=1
        )

        # When
        item_rule = item_rule_manager.get_item_rule(item_rule_config)

        # Then
        assert isinstance(item_rule, IItemRule)
        assert hasattr(item_rule_manager, "_item_rules")
        assert len(item_rule_manager._item_rules) == 1
