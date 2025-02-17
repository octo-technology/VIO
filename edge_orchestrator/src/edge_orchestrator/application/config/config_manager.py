import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from fastapi import HTTPException
from pydantic import ValidationError

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self._station_configs: Dict[str, StationConfig] = {}
        self._active_station_name: Optional[str] = os.getenv("ACTIVE_CONFIG_NAME", "config_1")
        self._logger = logging.getLogger(__name__)
        self._config_dir = Path(os.getenv("CONFIG_DIR", "config")).resolve()
        self._load_all_configs()

    def _load_all_configs(self) -> StationConfig:
        self._station_configs = {}
        if not self._config_dir.exists():
            self._logger.warning("No config directory found, creating it.")
            self._config_dir.mkdir(parents=True)
            return

        found_active_station_config = False
        for json_config_path in self._config_dir.iterdir():
            try:
                if json_config_path.is_file():
                    with json_config_path.open() as f:
                        station_config = StationConfig(**json.load(f))
                        self._station_configs[station_config.station_name] = station_config
                        if station_config.station_name == self._active_station_name:
                            self._active_station_name = station_config.station_name
                            found_active_station_config = True
            except (ValidationError, Exception):
                self._logger.exception(
                    f"The json station config file is invalid. Fix it or delete it: {json_config_path.as_posix()}"
                )
        if not found_active_station_config:
            self._logger.warning(
                f"No active json station config found at {(self._config_dir/self._active_station_name).with_suffix('.json').as_posix()}"
            )
        else:
            self._logger.info(f"Active station config found and set: {station_config.station_name}")

    def _save_config_as_json(self, station_config: StationConfig):
        with (self._config_dir / f"{station_config.station_name}.json").open("w") as f:
            f.write(station_config.model_dump_json(exclude_none=True))

    def set_config(self, new_station_config: StationConfig):
        new_active_station_name = new_station_config.station_name
        if new_active_station_name in self._station_configs:
            self._logger.warning(f"Overwritting existing station config name: {self._active_station_name}")
        self._active_station_name = new_active_station_name
        self._station_configs[new_active_station_name] = new_station_config
        self._save_config_as_json(new_station_config)

    def get_config(self) -> Optional[StationConfig]:
        return self._station_configs.get(self._active_station_name)

    def reload_configs(self):
        self._load_all_configs()

    @property
    def all_configs(self) -> Dict[str, StationConfig]:
        return self._station_configs

    def _is_an_existing_config_name(self, station_name: str) -> bool:
        if station_name not in self.all_configs:
            return False
        return True

    def set_config_by_name(self, station_name: str):
        if not self._is_an_existing_config_name(station_name):
            raise HTTPException(
                status_code=422,
                detail=f"{station_name} is not one of existing station names: {self.get_all_config_names()}",
            )
        self._active_station_name = station_name
