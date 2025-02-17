from pytest import fixture

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


# TODO: see where we define in tests redondant configs to centralize them here
@fixture(scope="function")
def station_config() -> StationConfig:
    return StationConfig(
        station_name="test_station",
        camera_configs={},
        binary_storage_config=StorageConfig(),
        metadata_storage_config=StorageConfig(),
        item_rule_config=ItemRuleConfig(
            item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
        ),
    )
