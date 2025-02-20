from unittest.mock import MagicMock, patch

from edge_orchestrator.domain.models.station_config import StationConfig
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

    @patch("edge_orchestrator.infrastructure.adapters.metadata_storage.gcp_metadata_storage.storage.Client")
    def test_should_return_expected_metadata_storage_and_store_it_as_attribute(
        self, mock_storage_client, station_config: StationConfig
    ):
        # Given
        mock_client_instance = MagicMock()
        mock_bucket = MagicMock()
        mock_client_instance.get_bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client_instance

        storage_type_metadata_storage_classes = [
            (StorageType.FILESYSTEM, FileSystemMetadataStorage),
            (StorageType.AWS, AWSMetadataStorage),
            (StorageType.AZURE, AzureMetadataStorage),
            (StorageType.GCP, GCPMetadataStorage),
        ]
        metadata_storage_manager = MetadataStorageManager(MetadataStorageFactory())
        # When
        for storage_type, metadata_storage_class in storage_type_metadata_storage_classes:
            if storage_type in [StorageType.AWS, StorageType.AZURE, StorageType.GCP]:
                station_config.metadata_storage_config = StorageConfig(
                    storage_type=storage_type, bucket_name="test_bucket"
                )
            else:
                station_config.metadata_storage_config = StorageConfig(storage_type=storage_type)

            metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
            assert isinstance(metadata_storage, metadata_storage_class)

        # Then
        assert hasattr(metadata_storage_manager, "_metadata_storages")
        assert len(metadata_storage_manager._metadata_storages) == 4
        for storage_type, _ in storage_type_metadata_storage_classes:
            assert storage_type in metadata_storage_manager._metadata_storages

        if storage_type == StorageType.GCP:
            mock_storage_client.assert_called_once()
            mock_client_instance.get_bucket.assert_called_once_with(station_config.metadata_storage_config.bucket_name)
