from functools import lru_cache
from pathlib import Path

from application.config import get_settings
from application.dto.station_config import StationConfig
from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.domain.ports.model_forward import ModelForward
from edge_orchestrator.domain.ports.telemetry_sink import TelemetrySink
from edge_orchestrator.domain.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.use_cases.uploader import Uploader
from edge_orchestrator.infrastructure.binary_storage.binary_storage_factory import (
    BinaryStorageFactory,
)
from edge_orchestrator.infrastructure.metadata_storage.metadata_storage_factory import (
    MetadataStorageFactory,
)
from edge_orchestrator.infrastructure.model_forward.model_forward_factory import (
    ModelForwardFactory,
)
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from edge_orchestrator.infrastructure.telemetry_sink.telemetry_sink_factory import (
    TelemetrySinkFactory,
)


@lru_cache()
def get_supervisor() -> Supervisor:
    return Supervisor(
        get_binary_storage(),
        get_edge_station(),
        get_metadata_storage(),
        get_model_forward(),
        get_station_config(),
        get_telemetry_sink(),
    )


@lru_cache()
def get_uploader() -> Uploader:
    return Uploader(
        get_metadata_storage(),
        get_binary_storage(),
    )


def _get_active_config_name(active_config_path: Path) -> str:
    if active_config_path.exists():
        with open(active_config_path, "r") as active_config:
            return active_config.read().strip()
    else:
        return "no_active_configuration"


@lru_cache()
def get_station_config(
    try_setting_station_config_from_file: bool = True,
) -> StationConfig:
    settings = get_settings()
    station_config = JsonStationConfig(
        settings.station_configs_folder, settings.data_folder
    )
    if try_setting_station_config_from_file:
        station_config = set_station_config_from_file(
            station_config, settings.active_config_path
        )
    return station_config


def set_station_config_from_file(
    station_config: StationConfig, active_config_path: Path
) -> StationConfig:
    active_config_name = _get_active_config_name(active_config_path)
    station_config.set_station_config(active_config_name)
    return station_config


@lru_cache()
def get_binary_storage() -> BinaryStorage:
    station_config = get_station_config()
    return BinaryStorageFactory.get_binary_storage(
        station_config.active_config["binary_storage"].get("type"),
        **station_config.active_config["binary_storage"].get("params", {}),
    )


@lru_cache()
def get_metadata_storage() -> MetadataStorage:
    station_config = get_station_config()
    return MetadataStorageFactory.get_metadata_storage(
        station_config.active_config["metadata_storage"]["type"],
        **station_config.active_config["metadata_storage"].get("params", {}),
    )


@lru_cache()
def get_edge_station() -> EdgeStation:
    return EdgeStation(get_station_config())


@lru_cache()
def get_model_forward() -> ModelForward:
    station_config = get_station_config()
    return ModelForwardFactory.get_model_forward(
        station_config.active_config["model_forward"]["type"],
        **station_config.active_config["model_forward"].get("params", {}),
    )


@lru_cache()
def get_telemetry_sink() -> TelemetrySink:
    station_config = get_station_config()
    return TelemetrySinkFactory.get_telemetry_sink(
        station_config.active_config["telemetry_sink"]["type"],
        **station_config.active_config["telemetry_sink"].get("params", {}),
    )
