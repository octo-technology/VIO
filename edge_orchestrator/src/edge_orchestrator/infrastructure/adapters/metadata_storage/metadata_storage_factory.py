import logging

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager


class MetadataStorageFactory(IMetadataStorageFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_metadata_storage(self, station_config: StationConfig) -> IMetadataStorage:
        storing_path_manager = StoringPathManager(station_config.metadata_storage_config, station_config.station_name)

        if station_config.metadata_storage_config.storage_type == StorageType.FILESYSTEM.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.filesystem_metadata_storage import (
                FileSystemMetadataStorage,
            )

            return FileSystemMetadataStorage(station_config, storing_path_manager)
        elif station_config.metadata_storage_config.storage_type == StorageType.AWS.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.aws_metadata_storage import (
                AWSMetadataStorage,
            )

            return AWSMetadataStorage(station_config, storing_path_manager)
        elif station_config.metadata_storage_config.storage_type == StorageType.GCP.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.gcp_metadata_storage import (
                GCPMetadataStorage,
            )

            return GCPMetadataStorage(station_config, storing_path_manager)
        elif station_config.metadata_storage_config.storage_type == StorageType.AZURE.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.azure_metadata_storage import (
                AzureMetadataStorage,
            )

            return AzureMetadataStorage(station_config, storing_path_manager)
        else:
            raise ValueError(
                f"Metadata storage type {station_config.metadata_storage_config.storage_type} is not supported"
            )
