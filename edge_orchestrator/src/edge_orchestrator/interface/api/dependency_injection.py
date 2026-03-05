from fastapi import HTTPException, Request

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.data_gathering import DataGathering
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)


def get_config() -> StationConfig:
    manager = ConfigManager()
    config = manager.get_config()
    if not config:
        raise HTTPException(status_code=400, detail="No active configuration set")
    return config


def get_supervisor(request: Request) -> Supervisor:
    return request.app.state.supervisor


def get_data_gathering(request: Request) -> DataGathering:
    return request.app.state.data_gathering


def get_binary_storage_manager(request: Request) -> IBinaryStorageManager:
    return request.app.state.binary_storage_manager


def get_metadata_storage_manager(request: Request) -> IMetadataStorageManager:
    return request.app.state.metadata_storage_manager
