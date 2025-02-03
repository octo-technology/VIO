from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)


class TestFileSystemBinaryStorage:
    def test_save_item_binaries_should_do_nothing_without_binaries(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        binary_storage = FileSystemBinaryStorage(storage_config)
        item_id = UUID("00000000-0000-0000-0000-000000000002")

        item = Item(
            id=item_id,
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        assert len(list((target_directory / str(item.id)).iterdir())) == 0

    def test_save_item_binaries_should_write_images_on_filesystem(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        binary_storage = FileSystemBinaryStorage(storage_config)
        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
            binaries={"camera_#1": expected_picture, "camera_#2": expected_picture},
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        path_to_pictures = [
            target_directory / str(item.id) / "camera_#1.jpg",
            target_directory / str(item.id) / "camera_#2.jpg",
        ]
        for path_to_picture in path_to_pictures:
            assert path_to_picture.is_file()
            actual_picture = path_to_picture.open("rb").read()
            assert actual_picture == expected_picture

    def test_save_item_binaries_with_prefix_should_write_images_on_filesystem(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        prefix = "station_#1"
        storage_config = StorageConfig(target_directory=target_directory, prefix=prefix)
        binary_storage = FileSystemBinaryStorage(storage_config)
        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
            binaries={"camera_#1": expected_picture},
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        path_to_picture = target_directory / prefix / str(item.id) / "camera_#1.jpg"
        assert path_to_picture.is_file()
        actual_picture = path_to_picture.open("rb").read()
        assert actual_picture == expected_picture

    def test_get_item_binaries_should_return_item_binaries(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        binary_storage = FileSystemBinaryStorage(storage_config)

        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")
        item_storage_folder = target_directory / str(item_id)
        item_storage_folder.mkdir()
        with (item_storage_folder / "camera_#1.jpg").open("wb") as f1, (item_storage_folder / "camera_#2.jpg").open(
            "wb"
        ) as f2:
            f1.write(expected_picture)
            f2.write(expected_picture)
        expected_camera_ids = ["camera_#1", "camera_#2"]

        # When
        actual_binaries = binary_storage.get_item_binaries(item_id)

        # Then
        assert len(actual_binaries) == 2
        for i, (actual_camera_id, actual_binary) in enumerate(actual_binaries.items()):
            assert actual_camera_id == expected_camera_ids[i]
            assert actual_binary == expected_picture
