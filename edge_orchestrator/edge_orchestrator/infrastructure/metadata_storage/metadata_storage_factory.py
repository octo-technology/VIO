from functools import lru_cache
from typing import Dict, Type, Optional, Any

from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.infrastructure.metadata_storage.azure_container_metadata_storage import (
    AzureContainerMetadataStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.filesystem_metadata_storage import (
    FileSystemMetadataStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.gcp_bucket_metadata_storage import (
    GCPBucketMetadataStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.in_memory_metadata_storage import (
    InMemoryMetadataStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.mongo_db_metadata_storage import (
    MongoDbMetadataStorage,
)
from infrastructure.filesystem_helpers import get_tmp_path

AVAILABLE_METADATA_STORAGES: Dict[str, Type[MetadataStorage]] = {
    "azure_container": AzureContainerMetadataStorage,
    "filesystem": FileSystemMetadataStorage,
    "gcp_bucket": GCPBucketMetadataStorage,
    "in_memory": InMemoryMetadataStorage,
    "mongo_db": MongoDbMetadataStorage,
}


class MetadataStorageFactory:
    @staticmethod
    @lru_cache()
    def get_metadata_storage(
        metadata_storage_type: Optional[str] = "filesystem",
        **metadata_storage_config: Optional[Dict[str, Any]],
    ) -> MetadataStorage:
        if not metadata_storage_type:
            metadata_storage_type["src_directory"] = get_tmp_path()
        try:
            # return AVAILABLE_METADATA_STORAGES[metadata_storage_type]()
            return AVAILABLE_METADATA_STORAGES[metadata_storage_type](
                **metadata_storage_config
            )
        except KeyError as err:
            raise ValueError(
                f"Unknown metadata storage type: {metadata_storage_type}"
            ) from err
