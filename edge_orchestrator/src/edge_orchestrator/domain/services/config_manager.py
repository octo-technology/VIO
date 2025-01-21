import logging
from typing import Dict, Optional

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self._station_configs: Dict[str, StationConfig] = {}
        self._active_station_config: Optional[str] = None
        self._logger = logging.getLogger(__name__)

    def set_config(self, station_config: StationConfig):
        self._active_station_config = station_config.station_profile
        if station_config.station_profile not in self._station_configs:
            self._station_configs[station_config.station_profile] = station_config

    def get_config(self) -> Optional[StationConfig]:
        return self._station_configs.get(self._active_station_config)

    def get_all_configs(self) -> Dict[str, StationConfig]:
        return self._station_configs
