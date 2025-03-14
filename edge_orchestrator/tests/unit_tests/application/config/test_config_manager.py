import os
from pathlib import Path

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class TestConfigManager:

    def test_config_manager_should_load_existing_active_config_from_env_variable_and_log(
        self, tmp_path: Path, cleanup_singleton, caplog
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        station_config = StationConfig(
            station_name="test_station",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = (config_dir / station_config.station_name).with_suffix(".json")
        with config_filepath.open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))
        os.environ["ACTIVE_CONFIG_NAME"] = station_config.station_name

        # When
        with caplog.at_level("INFO"):
            config_manager = ConfigManager()

        # Then
        active_station_config = config_manager.get_config()
        assert (
            active_station_config is not None
            and isinstance(active_station_config, StationConfig)
            and active_station_config == station_config
        )
        assert len(config_manager.all_configs) == 1 and active_station_config.station_name in config_manager.all_configs
        caplog_messages = [(record.msg, record.levelname) for record in caplog.records]
        assert (f"Active station config found and set: {station_config.station_name}", "INFO") in caplog_messages

    def test_config_manager_should_log_warning_with_no_config_dir(self, tmp_path: Path, caplog, cleanup_singleton):
        # Given
        unexisting_config_dir = tmp_path / "config"
        os.environ["CONFIG_DIR"] = unexisting_config_dir.as_posix()

        # When
        with caplog.at_level("WARNING"):
            config_manager = ConfigManager()

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is None
        assert (
            f"No config directory found, creating it.",
            "WARNING",
        ) in log_messages

    def test_config_manager_should_log_warning_with_no_active_config_found(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        os.environ["ACTIVE_CONFIG_NAME"] = "config_1"

        # When
        with caplog.at_level("WARNING"):
            config_manager = ConfigManager()

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is None
        assert (
            f"No active json station config found at {(config_dir/'config_1').with_suffix('.json').as_posix()}",
            "WARNING",
        ) in log_messages

    def test_config_manager_should_log_exception_with_bad_config_on_disk(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        config_filepath = config_dir / "bad_config.json"
        with (config_filepath).open("w") as f:
            f.write("{'bad': 'config'}")

        # When
        with caplog.at_level("ERROR"):
            config_manager = ConfigManager()

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
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        station_config_1 = StationConfig(
            station_name="test_station_1",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = config_dir / f"{station_config_1.station_name}.json"
        with config_filepath.open("w") as f:
            f.write(station_config_1.model_dump_json(exclude_none=True))
        os.environ["ACTIVE_CONFIG_NAME"] = station_config_1.station_name

        station_config_2 = StationConfig(
            station_name="test_station_2",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_manager = ConfigManager()

        # When
        config_manager.set_config(station_config_2)

        # Then
        active_station_config = config_manager.get_config()
        assert (
            active_station_config is not None
            and isinstance(active_station_config, StationConfig)
            and active_station_config == station_config_2
        )
        assert (
            len(config_manager.all_configs) == 2
            and station_config_1.station_name in config_manager.all_configs
            and station_config_2.station_name in config_manager.all_configs
        )

    def test_config_manager_should_write_active_config_on_disk(self, tmp_path: Path, cleanup_singleton):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        station_config = StationConfig(
            station_name="test_station_1",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_manager = ConfigManager()

        # When
        config_manager.set_config(station_config)

        # Then
        active_station_config = config_manager.get_config()
        config_filepath = config_dir / f"{station_config.station_name}.json"
        assert active_station_config is station_config
        assert config_filepath.exists()

    def test_config_manager_should_overwrite_existing_config_with_same_name(
        self, tmp_path: Path, caplog, cleanup_singleton
    ):
        # Given
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        os.environ["CONFIG_DIR"] = config_dir.as_posix()
        station_config = StationConfig(
            station_name="test_station",
            camera_configs={},
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )
        config_filepath = config_dir / f"{station_config.station_name}.json"
        with config_filepath.open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))
        os.environ["ACTIVE_CONFIG_NAME"] = station_config.station_name

        config_manager = ConfigManager()
        new_camera_config = {
            "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.FAKE, source_directory="fake")
        }

        # When
        with caplog.at_level("WARNING"):
            station_config.camera_configs = new_camera_config
            config_manager.set_config(station_config)

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        active_station_config = config_manager.get_config()
        assert active_station_config is station_config
        assert active_station_config.camera_configs == new_camera_config
        assert ("Overwritting existing station config name: test_station", "WARNING") in log_messages
