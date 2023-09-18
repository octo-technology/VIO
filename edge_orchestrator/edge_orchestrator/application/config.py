import json
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import yaml
from pydantic_settings import BaseSettings

from application.dto.station_config import StationConfig
from constants import ACTIVE_CONFIG_FILE_PATH


class Settings(BaseSettings):
    app_name: str = "edge-orchestrator API"
    url_prefix: str = "/api/v1"

    # root_dir: Path = Path(__file__).resolve().parents[2]
    # station_configs_folder: Path = root_dir / "config" / "station_configs"
    # data_folder: Path = root_dir / "data"
    # active_config_path: Path = root_dir / "config" / ".active_config"
    #
    # model_config = SettingsConfigDict(env_file=".env")


class _AbstractConfigReader(ABC):
    def __init__(self, path: Path):
        self._path = path
        self.config = self.get_config()

    def get_config(self) -> StationConfig:
        return self._read_file()

    @abstractmethod
    def _read_file(self) -> StationConfig:
        raise NotImplementedError("Not implemented")


class YamlConfigReader(_AbstractConfigReader):
    def _read_file(self) -> StationConfig:
        content = yaml.load(self._path.read_text(encoding="utf-8"), yaml.SafeLoader)
        return StationConfig.from_payload(content)


class JsonConfigReader(_AbstractConfigReader):
    def _read_file(self) -> StationConfig:
        _content = json.loads(self._path.read_text(encoding="utf-8"))
        return self.read_content(_content)

    @staticmethod
    def read_content(content: Dict[str, Any]) -> StationConfig:
        return StationConfig.from_payload(content)


class ConfigReader:
    def __init__(self, path: Path):
        self._path = path
        self._reader = self._define_reader()

    def _define_reader(self) -> _AbstractConfigReader:
        if self._path.suffixes[0] == ".json":
            return JsonConfigReader(self._path)
        elif self._path.suffixes[0] in [".yaml", ".yml"]:
            return YamlConfigReader(self._path)
        raise Exception(
            f"Unexpected extension of the deployment file: {self._path}. "
            f"Please check the documentation for supported extensions."
        )

    def get_config(self) -> StationConfig:
        return self._reader.config


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    config_reader = ConfigReader(ACTIVE_CONFIG_FILE_PATH)
    config = config_reader.get_config()
    return settings
