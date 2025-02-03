import json
import logging
from pathlib import Path
from typing import Dict, Optional

from pydantic import ValidationError

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    CONFIG_DIR = Path("config").resolve()
    ACTIVE_CONFIG_FILEPATH = CONFIG_DIR / "active_station_config.json"

    def __init__(self):
        self._station_configs: Dict[str, StationConfig] = {}
        self._active_station_config: Optional[str] = None
        self._logger = logging.getLogger(__name__)
        self._load_all_configs()

    def _load_all_configs(self) -> StationConfig:
        if not self.CONFIG_DIR.exists():
            self._logger.warning("No config directory found, creating it.")
            self.CONFIG_DIR.mkdir(parents=True)
            return

        found_active_station_config = False
        for json_config_path in self.CONFIG_DIR.iterdir():
            try:
                with json_config_path.open() as f:
                    station_config = StationConfig(**json.load(f))
                    self._station_configs[station_config.station_profile] = station_config
                    if json_config_path == self.ACTIVE_CONFIG_FILEPATH:
                        self._active_station_config = station_config.station_profile
                        found_active_station_config = True
            except (ValidationError, Exception):
                self._logger.exception(
                    f"The json station config file is invalid. Fix it or delete it: {json_config_path.as_posix()}"
                )
        if not found_active_station_config:
            self._logger.warning(f"No active json station config found in {self.ACTIVE_CONFIG_FILEPATH}")

    def _save_config_as_json(self, station_config: StationConfig):
        with (self.CONFIG_DIR / f"{station_config.station_profile}.json").open("w") as f:
            f.write(station_config.model_dump_json())

    def _make_active_config_point_on(self, station_config: StationConfig):
        if self.ACTIVE_CONFIG_FILEPATH.exists():
            self.ACTIVE_CONFIG_FILEPATH.unlink()
        self.ACTIVE_CONFIG_FILEPATH.symlink_to(self.CONFIG_DIR / f"{station_config.station_profile}.json")

    def set_config(self, station_config: StationConfig):
        self._active_station_config = station_config.station_profile
        if station_config.station_profile not in self._station_configs:
            self._station_configs[station_config.station_profile] = station_config
            self._save_config_as_json(station_config)
        self._make_active_config_point_on(station_config)

    def get_config(self) -> Optional[StationConfig]:
        return self._station_configs.get(self._active_station_config)

    def get_all_configs(self) -> Dict[str, StationConfig]:
        return self._station_configs
