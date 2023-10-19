from domain.models.business_rule.item_rule.item_rule_factory import get_item_rule

from edge_orchestrator.domain.models.decision import Decision


class TestItemBusinessRule:
    def test_item_decision_should_return_decision_ko_when_one_or_more_than_one_camera_decision_is_ko(
        self,
    ):  # noqa
        # Given
        camera_decisions = {"camera_id1": "KO", "camera_id2": "OK", "camera_id3": "OK"}

        # When
        item_rule_name = "min_threshold_ko_rule"
        item_rule_parameters = {"threshold": 1}

        item_rule = get_item_rule(item_rule_name)(**item_rule_parameters)
        item_decision = item_rule.get_item_decision(camera_decisions)

        # Then
        assert item_decision == Decision.KO

    def test_item_decision_should_return_decision_ok_when_more_than_50_pct_of_camera_decisions_are_ok(
        self,
    ):  # noqa
        # Given
        camera_decisions = {"camera_id1": "OK", "camera_id2": "OK", "camera_id3": "OK"}

        # When
        item_rule_name = "min_threshold_ok_ratio_rule"
        item_rule_parameters = {"min_threshold": 0.5}

        item_rule = get_item_rule(item_rule_name)(**item_rule_parameters)
        item_decision = item_rule.get_item_decision(camera_decisions)

        # Then
        assert item_decision == Decision.OK
