from unittest.mock import patch

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.infrastructure.binary_storage.memory_binary_storage import (
    MemoryBinaryStorage,
)


class TestMemoryBinaryStorage:
    @patch("edge_orchestrator.domain.models.item.generate_id")
    def test_save_item_binaries_should_write_image_in_memory(self, generate_id_mocked):
        # Given
        config_name_mocked = "test_config"
        generate_id_mocked.return_value = "my_item_id"
        binary_storage = MemoryBinaryStorage()
        expected_picture = bytes([0, 1, 2, 3, 4])
        item = Item(
            serial_number="serial_number",
            category="category",
            cameras_metadata={},
            binaries={"my_picture_name": expected_picture},
            dimensions=[100, 100],
        )

        # When
        binary_storage.save_item_binaries(item, config_name_mocked)

        # Then
        assert binary_storage.binaries == {"my_item_id": {"my_picture_name": expected_picture}}

    def test_get_item_binary_should_return_requested_item_binary(self):
        # Given
        config_name_mocked = "test_config"
        binary_storage = MemoryBinaryStorage()
        expected_picture = bytes([0, 1, 2, 3, 4])
        another_picture = bytes([5, 6, 7, 8, 9])
        binary_storage.binaries = {
            "my_item_id": {
                "my_picture_name_1": expected_picture,
                "my_picture_name_2": another_picture,
            }
        }

        # When
        binary = binary_storage.get_item_binary("my_item_id", "my_picture_name_1", config_name_mocked)

        # Then
        assert binary == expected_picture

    def test_get_item_binaries_should_return_all_item_binaries_names(self):
        # Given
        config_name_mocked = "test_config"
        binary_storage = MemoryBinaryStorage()
        expected_picture_1 = bytes([0, 1, 2, 3, 4])
        expected_picture_2 = bytes([5, 6, 7, 8, 9])
        binary_storage.binaries = {
            "my_item_id": {
                "my_picture_name_1": expected_picture_1,
                "my_picture_name_2": expected_picture_2,
            }
        }

        # When
        binaries_names = binary_storage.get_item_binaries("my_item_id", config_name_mocked)

        # Then
        assert binaries_names == ["my_picture_name_1", "my_picture_name_2"]
