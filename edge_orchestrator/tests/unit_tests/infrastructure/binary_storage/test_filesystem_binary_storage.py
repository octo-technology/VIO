from pathlib import Path
from unittest.mock import patch

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.infrastructure.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)


class TestFileSystemBinaryStorage:
    @patch("edge_orchestrator.domain.models.item.generate_id")
    def test_save_item_binaries_should_write_image_on_filesystem(
        self, generate_id_mocked, tmpdir
    ):
        # Given
        generate_id_mocked.return_value = "my_item_id"
        src_directory_path = Path(tmpdir.mkdir("binaries"))
        binary_storage = FileSystemBinaryStorage(src_directory_path)
        expected_picture = bytes([0, 1, 2, 3, 4])
        active_config_name = "detection_model"

        item = Item(
            serial_number="serial_number",
            category="category",
            cameras_metadata={},
            binaries={"camera_id": expected_picture},
        )

        # When
        binary_storage.save_item_binaries(item, active_config_name)

        # Then
        path_to_my_picture = (
            src_directory_path / active_config_name / "my_item_id" / "camera_id.jpg"
        )
        assert path_to_my_picture.is_file()
        actual_picture = path_to_my_picture.open("rb").read()
        assert actual_picture == expected_picture

    def test_get_item_binary_should_return_requested_item_binary(self, tmpdir):
        # Given
        src_directory_path = Path(tmpdir.mkdir("binaries"))
        binary_storage = FileSystemBinaryStorage(src_directory_path)
        expected_picture = bytes([0, 1, 2, 3, 4])
        active_config_name = "detection_model"
        (src_directory_path / active_config_name / "my_item_id").mkdir(parents=True)
        with (
            src_directory_path / active_config_name / "my_item_id" / "camera_id.jpg"
        ).open("wb") as f:
            f.write(expected_picture)

        # When
        actual_binary = binary_storage.get_item_binary(
            "my_item_id", "camera_id", active_config_name
        )

        # Then
        assert actual_binary == expected_picture

    def test_get_item_binaries_should_return_all_item_binaries_names(self, tmpdir):
        # Given
        src_directory_path = Path(tmpdir.mkdir("binaries"))
        binary_storage = FileSystemBinaryStorage(src_directory_path)
        expected_picture_1 = bytes([0, 1, 2, 3, 4])
        expected_picture_2 = bytes([5, 6, 7, 8, 9])
        active_config_name = "detection_model"

        (src_directory_path / active_config_name / "my_item_id").mkdir(parents=True)

        with (
            src_directory_path / active_config_name / "my_item_id" / "camera_id1.jpg"
        ).open("wb") as f_1:
            with (
                (
                    src_directory_path
                    / active_config_name
                    / "my_item_id"
                    / "camera_id2.jpg"
                )
            ).open("wb") as f_2:
                f_1.write(expected_picture_1)
                f_2.write(expected_picture_2)

        # When
        binaries_names = binary_storage.get_item_binaries(
            "my_item_id", active_config_name
        )

        # Then
        assert set(binaries_names) == {
            "camera_id1.jpg",
            "camera_id2.jpg",
        }
