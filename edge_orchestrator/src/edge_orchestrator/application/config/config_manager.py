import json
import logging
from pathlib import Path
from typing import Dict, Optional

from pydantic import ValidationError

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self, config_dir: Optional[Path] = Path("config").resolve()):
        self._station_configs: Dict[str, StationConfig] = {}
        self._active_station_profile: Optional[str] = None
        self._logger = logging.getLogger(__name__)
        self._config_dir = config_dir
        self._active_config_filepath = config_dir / "active_station_config.json"
        self._load_all_configs()

    def _load_all_configs(self) -> StationConfig:
        if not self._config_dir.exists():
            self._logger.warning("No config directory found, creating it.")
            self._config_dir.mkdir(parents=True)
            return

        found_active_station_config = False
        for json_config_path in self._config_dir.iterdir():
            try:
                with json_config_path.open() as f:
                    station_config = StationConfig(**json.load(f))
                    self._station_configs[station_config.station_profile] = station_config
                    if json_config_path == self._active_config_filepath:
                        self._active_station_profile = station_config.station_profile
                        found_active_station_config = True
            except (ValidationError, Exception):
                self._logger.exception(
                    f"The json station config file is invalid. Fix it or delete it: {json_config_path.as_posix()}"
                )
        if not found_active_station_config:
            self._logger.warning(f"No active json station config found at {self._active_config_filepath.as_posix()}")

    def _save_config_as_json(self, station_config: StationConfig):
        with (self._config_dir / f"{station_config.station_profile}.json").open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))

    def _make_active_config_file_point_on(self, station_config: StationConfig):
        self._active_config_filepath.unlink(missing_ok=True)
        self._active_config_filepath.symlink_to(self._config_dir / f"{station_config.station_profile}.json")

    def set_config(self, new_station_config: StationConfig):
        new_active_station_profile = new_station_config.station_profile
        if new_active_station_profile in self._station_configs:
            self._logger.warning(f"Overwritting existing station config profile: {self._active_station_profile}")
        self._active_station_profile = new_active_station_profile
        self._station_configs[new_active_station_profile] = new_station_config
        self._save_config_as_json(new_station_config)
        self._make_active_config_file_point_on(new_station_config)

    def get_config(self) -> Optional[StationConfig]:
        return self._station_configs.get(self._active_station_profile)

    def get_all_configs(self) -> Dict[str, StationConfig]:
        return self._station_configs
