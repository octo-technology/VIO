from unittest.mock import Mock, patch

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage import (
    GCPBinaryStorage,
)
from tests.conftest import EDGE_NAME, TEST_DATA_FOLDER_PATH


class TestGCPBinaryStorage:
    @patch("edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage.storage")
    def test_save_item_binaries_should_write_image_in_gcp(self, mock_storage):
        # Given
        test_active_config_name = "test_config"
        test_camera_id = "1"
        test_file_path = TEST_DATA_FOLDER_PATH / EDGE_NAME / test_active_config_name / "item_2" / "camera_id1.jpg"
        item = Item.from_nothing()
        with open(test_file_path, "rb") as f:
            item.binaries = {test_camera_id: f}
        mock_gcs_client = mock_storage.Client.return_value
        mock_bucket = Mock()
        mock_gcs_client.get_bucket.return_value = mock_bucket
        gcs = GCPBinaryStorage(prefix=EDGE_NAME, active_config_name=test_active_config_name)

        # When
        gcs.save_item_binaries(item)

        # Then
        mock_storage.Client.assert_called_once()
        mock_bucket.blob.assert_called_once_with(
            f"{EDGE_NAME}/{test_active_config_name}/{item.id}/{test_camera_id}.jpg"
        )
        mock_bucket.blob.return_value.upload_from_string.assert_called_once_with(f, content_type="image/jpg")

    @patch("edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage.storage")
    def test_get_item_binary_should_return_image(self, mock_storage):
        # Given
        test_active_config_name = "test_config"
        test_camera_id = "1"
        test_file_path = TEST_DATA_FOLDER_PATH / EDGE_NAME / test_active_config_name / "item_2" / "camera_id1.jpg"
        item = Item.from_nothing()
        with open(test_file_path, "rb") as f:
            item.binaries = {test_camera_id: f}
        mock_gcs_client = mock_storage.Client.return_value
        mock_bucket = Mock()
        mock_gcs_client.get_bucket.return_value = mock_bucket
        gcs = GCPBinaryStorage(prefix=EDGE_NAME, active_config_name=test_active_config_name)
        gcs.save_item_binaries(item)

        # When
        gcs.get_item_binary(item.id, test_camera_id)

        # Then
        mock_storage.Client.assert_called_once()
        mock_bucket.get_blob.assert_called_once_with(
            f"{EDGE_NAME}/{test_active_config_name}/{item.id}/{test_camera_id}.jpg"
        )
