from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.infrastructure.adapters.metadata_storage.aws_metadata_storage import (
    AWSMetadataStorage,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.azure_metadata_storage import (
    AzureMetadataStorage,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.filesystem_metadata_storage import (
    FileSystemMetadataStorage,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.gcp_metadata_storage import (
    GCPMetadataStorage,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.metadata_storage_factory import (
    MetadataStorageFactory,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.metadata_storage_manager import (
    MetadataStorageManager,
)


class TestMetadataStorageManager:

    def test_should_return_expected_metadata_storage_and_store_it_as_attribute(
        self,
    ):
        # Given
        storage_type_metadata_storage_classes = [
            (StorageType.FILESYSTEM, FileSystemMetadataStorage),
            (StorageType.AWS, AWSMetadataStorage),
            (StorageType.AZURE, AzureMetadataStorage),
            (StorageType.GCP, GCPMetadataStorage),
        ]
        metadata_storage_manager = MetadataStorageManager(MetadataStorageFactory())

        # When
        for storage_type, metadata_storage_class in storage_type_metadata_storage_classes:
            metadata_storage_config = StorageConfig(storage_type=storage_type)
            metadata_storage = metadata_storage_manager.get_metadata_storage(metadata_storage_config)
            assert isinstance(metadata_storage, metadata_storage_class)

        # Then
        assert hasattr(metadata_storage_manager, "_metadata_storages")
        assert len(metadata_storage_manager._metadata_storages) == 4
        for storage_type, _ in storage_type_metadata_storage_classes:
            assert storage_type in metadata_storage_manager._metadata_storages
