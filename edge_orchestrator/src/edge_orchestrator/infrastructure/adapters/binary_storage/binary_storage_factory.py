import logging

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class BinaryStorageFactory(IBinaryStorageFactory):
    def __init__(self, storing_path_manager: StoringPathManager):
        self._logger = logging.getLogger(__name__)
        self._storing_path_manager = storing_path_manager

    def create_binary_storage(self, station_config: StationConfig) -> IBinaryStorage:
        if station_config.binary_storage_config.storage_type == StorageType.FILESYSTEM.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
                FileSystemBinaryStorage,
            )

            return FileSystemBinaryStorage(station_config, self._storing_path_manager)
        elif station_config.binary_storage_config.storage_type == StorageType.AWS.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.aws_binary_storage import (
                AWSBinaryStorage,
            )

            return AWSBinaryStorage(station_config, self._storing_path_manager)
        elif station_config.binary_storage_config.storage_type == StorageType.GCP.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage import (
                GCPBinaryStorage,
            )

            return GCPBinaryStorage(station_config, self._storing_path_manager)
        elif station_config.binary_storage_config.storage_type == StorageType.AZURE.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.azure_binary_storage import (
                AzureBinaryStorage,
            )

            return AzureBinaryStorage(station_config, self._storing_path_manager)
        else:
            raise Exception(f"Binary storage type {station_config.binary_storage_config.storage_type} not supported")
