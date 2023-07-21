from functools import lru_cache
from typing import Optional, Dict, Type, Any

from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.infrastructure.binary_storage.azure_container_binary_storage import (
    AzureContainerBinaryStorage,
)
from edge_orchestrator.infrastructure.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.binary_storage.gcp_bucket_binary_storage import (
    GCPBucketBinaryStorage,
)
from edge_orchestrator.infrastructure.binary_storage.in_memory_binary_storage import (
    InMemoryBinaryStorage,
)
from edge_orchestrator.infrastructure.filesystem_helpers import get_tmp_path

AVAILABLE_BINARY_STORAGES: Dict[str, Type[BinaryStorage]] = {
    "azure_container": AzureContainerBinaryStorage,
    "filesystem": FileSystemBinaryStorage,
    "gcp_bucket": GCPBucketBinaryStorage,
    "in_memory": InMemoryBinaryStorage,
}


class BinaryStorageFactory:
    @staticmethod
    @lru_cache()
    def get_binary_storage(
        binary_storage_type: Optional[str] = "filesystem",
        **binary_storage_config: Optional[Dict[str, Any]],
    ) -> BinaryStorage:
        if not binary_storage_config:
            binary_storage_config["src_directory"] = get_tmp_path()
        try:
            return AVAILABLE_BINARY_STORAGES[binary_storage_type](
                **binary_storage_config
            )
        except KeyError as err:
            raise ValueError(
                f"Unknown binary storage type: {binary_storage_type}"
            ) from err
