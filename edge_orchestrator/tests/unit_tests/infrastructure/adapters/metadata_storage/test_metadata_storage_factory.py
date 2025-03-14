from unittest.mock import MagicMock, patch

import pytest

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager
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


class TestMetadataStorageFactory:

    @pytest.mark.parametrize(
        "storage_type,metadata_storage_class",
        [
            (StorageType.FILESYSTEM, FileSystemMetadataStorage),
            (StorageType.AWS, AWSMetadataStorage),
            (StorageType.AZURE, AzureMetadataStorage),
            (StorageType.GCP, GCPMetadataStorage),
        ],
    )
    @patch("edge_orchestrator.infrastructure.adapters.metadata_storage.gcp_metadata_storage.storage.Client")
    def test_should_return_the_specified_metadata_storage_instance(
        self,
        mock_storage_client,
        storage_type: StorageType,
        metadata_storage_class: IMetadataStorage,
        station_config: StationConfig,
    ):
        # Given
        mock_client_instance = MagicMock()
        mock_bucket = MagicMock()
        mock_client_instance.get_bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client_instance

        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        metadata_storage_factory = MetadataStorageFactory(storing_path_manager)
        station_config.binary_storage_config.storage_type = storage_type

        # When
        metadata_storage = metadata_storage_factory.create_metadata_storage(station_config)

        # Then
        assert isinstance(metadata_storage, metadata_storage_class)
        assert hasattr(metadata_storage, "save_item_metadata")
        assert hasattr(metadata_storage, "get_item_metadata")

        if storage_type == StorageType.GCP:
            mock_storage_client.assert_called_once()
            mock_client_instance.get_bucket.assert_called_once_with(station_config.metadata_storage_config.bucket_name)
