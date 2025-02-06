import pytest

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.ports.item_rule.i_item_rule import IItemRule
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_factory import (
    ItemRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_ratio_rule import (
    MinThresholdRatioRule,
)
from edge_orchestrator.infrastructure.adapters.item_rule.min_threshold_rule import (
    MinThresholdRule,
)


class TestItemRuleFactory:

    @pytest.mark.parametrize(
        "item_rule_type,item_rule_class,decision",
        [
            (ItemRuleType.MIN_THRESHOLD_RULE, MinThresholdRule, Decision.OK),
            (ItemRuleType.MIN_THRESHOLD_RATIO_RULE, MinThresholdRatioRule, Decision.KO),
        ],
    )
    def test_should_return_the_specified_item_rule_instance(
        self, item_rule_type: ItemRuleType, item_rule_class: IItemRule, decision: Decision
    ):
        # Given
        item_rule_factory = ItemRuleFactory()
        item_rule_config = ItemRuleConfig(item_rule_type=item_rule_type, expected_decision=decision, threshold=1)

        # When
        item_rule = item_rule_factory.create_item_rule(item_rule_config)

        # Then
        assert isinstance(item_rule, item_rule_class)
        assert hasattr(item_rule, "apply_item_rules")
        assert hasattr(item_rule, "_get_item_decision")
