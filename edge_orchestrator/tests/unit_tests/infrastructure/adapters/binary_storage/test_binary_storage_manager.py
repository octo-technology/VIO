from unittest.mock import MagicMock, patch

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.infrastructure.adapters.binary_storage.aws_binary_storage import (
    AWSBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.azure_binary_storage import (
    AzureBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.binary_storage_factory import (
    BinaryStorageFactory,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.binary_storage_manager import (
    BinaryStorageManager,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage import (
    GCPBinaryStorage,
)


class TestBinaryStorageManager:

    @patch("edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage.storage.Client")
    def test_should_return_expected_binary_storage_and_store_it_as_attribute(
        self, mock_storage_client, station_config: StationConfig
    ):
        mock_client_instance = MagicMock()
        mock_bucket = MagicMock()
        mock_client_instance.get_bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client_instance

        # Given
        storage_type_binary_storage_classes = [
            (StorageType.FILESYSTEM, FileSystemBinaryStorage),
            (StorageType.AWS, AWSBinaryStorage),
            (StorageType.AZURE, AzureBinaryStorage),
            (StorageType.GCP, GCPBinaryStorage),
        ]
        binary_storage_manager = BinaryStorageManager(BinaryStorageFactory())

        # When
        for storage_type, binary_storage_class in storage_type_binary_storage_classes:
            if storage_type in [StorageType.AWS, StorageType.AZURE, StorageType.GCP]:
                station_config.binary_storage_config = StorageConfig(
                    storage_type=storage_type, bucket_name="test_bucket"
                )
            else:
                station_config.binary_storage_config = StorageConfig(storage_type=storage_type)

            binary_storage = binary_storage_manager.get_binary_storage(station_config)
            assert isinstance(binary_storage, binary_storage_class)

        # Then
        assert hasattr(binary_storage_manager, "_binary_storages")
        assert len(binary_storage_manager._binary_storages) == 4
        for storage_type, _ in storage_type_binary_storage_classes:
            assert storage_type in binary_storage_manager._binary_storages

        if storage_type == StorageType.GCP:
            mock_storage_client.assert_called_once()
            mock_client_instance.get_bucket.assert_called_once_with(station_config.binary_storage_config.bucket_name)
