from pathlib import Path

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class TestConfigManager:

    def test_config_manager_should_load_existing_active_config_from_disk(self, tmp_path: Path, cleanup_singleton):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        station_config = StationConfig(
            station_name="test_station",
            station_profile="test_profile",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = config_dir / f"{station_config.station_profile}.json"
        with config_filepath.open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))
            (config_dir / "active_station_config.json").symlink_to(config_filepath)

        # When
        config_manager = ConfigManager(config_dir)

        # Then
        active_station_config = config_manager.get_config()
        all_config = config_manager.get_all_configs()
        assert (
            active_station_config is not None
            and isinstance(active_station_config, StationConfig)
            and active_station_config == station_config
        )
        assert len(all_config) == 1 and active_station_config.station_profile in all_config

    def test_config_manager_should_log_warning_with_no_config_dir(self, tmp_path: Path, caplog, cleanup_singleton):
        # Given
        unexisting_config_dir = tmp_path / "config"

        # When
        with caplog.at_level("WARNING"):
            config_manager = ConfigManager(unexisting_config_dir)

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is None
        assert (
            f"No config directory found, creating it.",
            "WARNING",
        ) in log_messages

    def test_config_manager_should_log_warning_with_no_active_config_on_disk(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # When
        with caplog.at_level("WARNING"):
            config_manager = ConfigManager(config_dir)

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is None
        assert (
            f"No active json station config found at {(config_dir/'active_station_config.json').as_posix()}",
            "WARNING",
        ) in log_messages

    def test_config_manager_should_log_exception_with_bad_config_on_disk(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_filepath = config_dir / "bad_config.json"
        with (config_filepath).open("w") as f:
            f.write("{'bad': 'config'}")

        # When
        with caplog.at_level("ERROR"):
            config_manager = ConfigManager(config_dir)

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is None
        assert (
            f"The json station config file is invalid. Fix it or delete it: {config_filepath.as_posix()}",
            "ERROR",
        ) in log_messages

    def test_config_manager_should_set_new_config_as_active_config(self, tmp_path: Path, cleanup_singleton):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        station_config_1 = StationConfig(
            station_name="test_station",
            station_profile="test_profile_1",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = config_dir / f"{station_config_1.station_profile}.json"
        with config_filepath.open("w") as f:
            f.write(station_config_1.model_dump_json(exclude_none=True))
            (config_dir / "active_station_config.json").symlink_to(config_filepath)

        station_config_2 = StationConfig(
            station_name="test_station",
            station_profile="test_profile_2",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_manager = ConfigManager(config_dir)

        # When
        config_manager.set_config(station_config_2)

        # Then
        active_station_config = config_manager.get_config()
        all_config = config_manager.get_all_configs()
        assert (
            active_station_config is not None
            and isinstance(active_station_config, StationConfig)
            and active_station_config == station_config_2
        )
        assert (
            len(all_config) == 2
            and station_config_1.station_profile in all_config
            and station_config_2.station_profile in all_config
        )

    def test_config_manager_should_write_active_config_on_disk(self, tmp_path: Path, cleanup_singleton):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        station_config = StationConfig(
            station_name="test_station",
            station_profile="test_profile_1",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_manager = ConfigManager(config_dir)

        # When
        config_manager.set_config(station_config)

        # Then
        active_station_config = config_manager.get_config()
        config_filepath = config_dir / f"{station_config.station_profile}.json"
        active_config_filepath = config_dir / "active_station_config.json"
        assert active_station_config is station_config
        assert config_filepath.exists()
        assert active_config_filepath.exists()
        assert config_filepath.read_text() == active_config_filepath.read_text()

    def test_config_manager_should_overwrite_existing_config_with_same_profile(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        station_config = StationConfig(
            station_name="test_station",
            station_profile="test_profile_1",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = config_dir / f"{station_config.station_profile}.json"
        with config_filepath.open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))
            (config_dir / "active_station_config.json").symlink_to(config_filepath)

        config_manager = ConfigManager(config_dir)

        # When
        with caplog.at_level("WARNING"):
            station_config.station_name = "new_station_name"
            config_manager.set_config(station_config)

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is station_config
        assert active_station_config.station_name == "new_station_name"
        assert ("Overwritting existing station config profile: test_profile_1", "WARNING") in log_messages
