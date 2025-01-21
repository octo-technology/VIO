import logging

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)


class BinaryStorageFactory(IBinaryStorageFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_binary_storage(self, binary_storage_config: StorageConfig) -> IBinaryStorage:
        if binary_storage_config.storage_type == StorageType.FILESYSTEM.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
                FileSystemBinaryStorage,
            )

            return FileSystemBinaryStorage(binary_storage_config)
        elif binary_storage_config.storage_type == StorageType.AWS.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.aws_binary_storage import (
                AWSBinaryStorage,
            )

            return AWSBinaryStorage(binary_storage_config)
        elif binary_storage_config.storage_type == StorageType.GCP.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage import (
                GCPBinaryStorage,
            )

            return GCPBinaryStorage(binary_storage_config)
        elif binary_storage_config.storage_type == StorageType.AZURE.value:
            from edge_orchestrator.infrastructure.adapters.binary_storage.azure_binary_storage import (
                AzureBinaryStorage,
            )

            return AzureBinaryStorage(binary_storage_config)
        else:
            raise Exception(f"Binary storage type {binary_storage_config.storage_type} not supported")
