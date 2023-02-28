from unittest.mock import patch, Mock
from datetime import datetime

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage import GCPBinaryStorage

from tests.conftest import TEST_DATA_FOLDER_PATH


class TestGCPBinaryStorage:
    @patch('edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage.storage')
    def test_save_item_binaries_should_write_image_in_gcp(self, mock_storage):
        # Given
        test_camera_id = '1'
        test_file_path = TEST_DATA_FOLDER_PATH / 'item_2' / 'camera_id1.jpg'
        item = Item.from_nothing()
        with open(test_file_path, "rb") as f:
            item.binaries = {test_camera_id: f}
        mock_gcs_client = mock_storage.Client.return_value
        mock_bucket = Mock()
        mock_gcs_client.get_bucket.return_value = mock_bucket
        gcs = GCPBinaryStorage()

        # When
        gcs.save_item_binaries(item)

        # Then
        mock_storage.Client.assert_called_once()
        mock_bucket.blob.assert_called_once_with(
            f"{datetime.now().strftime('%d-%m-%Y')}_{item.id}/{test_camera_id}.jpg")
        mock_bucket.blob.return_value.upload_from_string.assert_called_once_with(f, content_type="image/jpg")
