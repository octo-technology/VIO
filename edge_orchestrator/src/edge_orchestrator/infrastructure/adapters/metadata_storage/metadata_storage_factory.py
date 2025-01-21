import logging

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)


class MetadataStorageFactory(IMetadataStorageFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_metadata_storage(self, storage_config: StorageConfig) -> IMetadataStorage:
        if storage_config.storage_type == StorageType.FILESYSTEM.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.filesystem_metadata_storage import (
                FileSystemMetadataStorage,
            )

            return FileSystemMetadataStorage(storage_config)
        elif storage_config.storage_type == StorageType.AWS.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.aws_metadata_storage import (
                AWSMetadataStorage,
            )

            return AWSMetadataStorage(storage_config)
        elif storage_config.storage_type == StorageType.GCP.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.gcp_metadata_storage import (
                GCPMetadataStorage,
            )

            return GCPMetadataStorage(storage_config)
        elif storage_config.storage_type == StorageType.AZURE.value:
            from edge_orchestrator.infrastructure.adapters.metadata_storage.azure_metadata_storage import (
                AzureMetadataStorage,
            )

            return AzureMetadataStorage(storage_config)
        else:
            raise ValueError(f"Metadata storage type {storage_config.storage_type} is not supported")
