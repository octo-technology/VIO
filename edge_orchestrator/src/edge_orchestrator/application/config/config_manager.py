import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import ValidationError

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self._station_configs: Dict[str, StationConfig] = {}
        self._active_station_name: Optional[str] = None
        self._logger = logging.getLogger(__name__)
        self._config_dir = Path(os.environ.get("CONFIG_DIR", "config")).resolve()
        self._active_config_filepath = self._config_dir / "active_station_config.json"
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
                    self._station_configs[station_config.station_name] = station_config
                    if json_config_path == self._active_config_filepath:
                        self._active_station_name = station_config.station_name
                        found_active_station_config = True
            except (ValidationError, Exception):
                self._logger.exception(
                    f"The json station config file is invalid. Fix it or delete it: {json_config_path.as_posix()}"
                )
        if not found_active_station_config:
            self._logger.warning(f"No active json station config found at {self._active_config_filepath.as_posix()}")

    def _save_config_as_json(self, station_config: StationConfig):
        with (self._config_dir / f"{station_config.station_name}.json").open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))

    def _make_active_config_file_point_on(self, station_config: StationConfig):
        self._active_config_filepath.unlink(missing_ok=True)
        self._active_config_filepath.symlink_to(self._config_dir / f"{station_config.station_name}.json")

    def set_config(self, new_station_config: StationConfig):
        new_active_station_name = new_station_config.station_name
        if new_active_station_name in self._station_configs:
            self._logger.warning(f"Overwritting existing station config name: {self._active_station_name}")
        self._active_station_name = new_active_station_name
        self._station_configs[new_active_station_name] = new_station_config
        self._save_config_as_json(new_station_config)
        self._make_active_config_file_point_on(new_station_config)

    def get_config(self) -> Optional[StationConfig]:
        return self._station_configs.get(self._active_station_name)

    def get_all_configs(self) -> Dict[str, StationConfig]:
        return self._station_configs

    def get_all_config_names(self) -> List[str]:
        return self._station_configs.keys() if len(self._station_configs) else []

    def _is_an_existing_station_name(self, station_name: str) -> bool:
        if station_name not in self.get_all_config_names():
            return False
        return True

    def set_config_by_name(self, station_name: str):
        if not self._is_an_existing_station_name(station_name):
            raise ValueError(f"{station_name} is not one of existing station names: {self.get_all_config_names()}")
        self._active_station_name = station_name
