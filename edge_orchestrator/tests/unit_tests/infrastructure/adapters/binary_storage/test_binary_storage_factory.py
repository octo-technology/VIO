from unittest.mock import MagicMock, patch

import pytest

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.models.storage.storage_type import StorageType
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.aws_binary_storage import (
    AWSBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.azure_binary_storage import (
    AzureBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.binary_storage_factory import (
    BinaryStorageFactory,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage import (
    GCPBinaryStorage,
)


class TestBinaryStorageFactory:

    @pytest.mark.parametrize(
        "storage_type,binary_storage_class",
        [
            (StorageType.FILESYSTEM, FileSystemBinaryStorage),
            (StorageType.AWS, AWSBinaryStorage),
            (StorageType.AZURE, AzureBinaryStorage),
            (StorageType.GCP, GCPBinaryStorage),
        ],
    )
    @patch("edge_orchestrator.infrastructure.adapters.binary_storage.gcp_binary_storage.storage.Client")
    def test_should_return_the_specified_binary_storage_instance(
        self,
        mock_storage_client,
        storage_type: StorageType,
        binary_storage_class: IBinaryStorage,
        station_config: StationConfig,
    ):
        # Given
        mock_client_instance = MagicMock()
        mock_bucket = MagicMock()
        mock_client_instance.get_bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client_instance

        binary_storage_config = StorageConfig(storage_type=storage_type)
        station_config.binary_storage_config = binary_storage_config
        binary_storage_factory = BinaryStorageFactory()

        # When
        binary_storage = binary_storage_factory.create_binary_storage(station_config)

        # Then
        assert isinstance(binary_storage, binary_storage_class)
        assert hasattr(binary_storage, "save_item_binaries")
        assert hasattr(binary_storage, "get_item_binaries")

        if storage_type == StorageType.GCP:
            mock_storage_client.assert_called_once()
            mock_client_instance.get_bucket.assert_called_once_with(
                station_config.binary_storage_config.bucket_name.as_posix()
            )
