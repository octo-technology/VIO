from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.item import Image, Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.storing_path_manager import StoringPathManager
from edge_orchestrator.infrastructure.adapters.binary_storage.filesystem_binary_storage import (
    FileSystemBinaryStorage,
)


class TestFileSystemBinaryStorage:
    def test_save_item_binaries_should_do_nothing_without_binaries(self, tmp_path: Path, station_config: StationConfig):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)
        item_id = UUID("00000000-0000-0000-0000-000000000002")

        item = Item(
            id=item_id,
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        assert len(list((target_directory / station_config.station_name).iterdir())) == 0

    def test_save_item_binaries_should_write_images_on_filesystem(self, tmp_path: Path, station_config: StationConfig):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)
        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
            binaries={
                "camera_#1": Image(image_bytes=expected_picture),
                "camera_#2": Image(image_bytes=expected_picture),
            },
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        path_to_pictures = [
            target_directory / station_config.station_name / f"{str(item.id)}_camera_#1.jpg",
            target_directory / station_config.station_name / f"{str(item.id)}_camera_#2.jpg",
        ]
        for path_to_picture in path_to_pictures:
            assert path_to_picture.is_file()
            actual_picture = path_to_picture.open("rb").read()
            assert actual_picture == expected_picture

    def test_save_item_binaries_with_target_directory_should_write_images_on_filesystem(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)
        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
            binaries={"camera_#1": Image(image_bytes=expected_picture)},
        )

        # When
        binary_storage.save_item_binaries(item)

        # Then
        path_to_picture = target_directory / station_config.station_name / f"{str(item.id)}_camera_#1.jpg"
        assert path_to_picture.is_file()
        actual_picture = path_to_picture.open("rb").read()
        assert actual_picture == expected_picture

    def test_get_item_binaries_should_return_item_binaries(self, tmp_path: Path, station_config: StationConfig):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)

        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")
        item_storage_folder = target_directory / station_config.station_name
        item_storage_folder.mkdir(parents=True)
        with (
            (item_storage_folder / f"{str(item_id)}_camera_#1.jpg").open("wb") as f1,
            (item_storage_folder / f"{str(item_id)}_camera_#2.jpg").open("wb") as f2,
        ):
            f1.write(expected_picture)
            f2.write(expected_picture)
        expected_camera_ids = [f"{str(item_id)}_camera_#1", f"{str(item_id)}_camera_#2"]

        # When
        actual_binaries = binary_storage.get_item_binaries(item_id)

        # Then
        assert len(actual_binaries) == 2
        for i, (actual_camera_id, actual_binary) in enumerate(sorted(actual_binaries.items())):
            assert actual_camera_id == expected_camera_ids[i]
            assert actual_binary == expected_picture

    def test_get_item_binary_names_should_return_binary_names(self, tmp_path: Path, station_config: StationConfig):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)

        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")
        item_storage_folder = target_directory / station_config.station_name
        item_storage_folder.mkdir(parents=True)
        with (
            (item_storage_folder / f"{str(item_id)}_camera_#1.jpg").open("wb") as f1,
            (item_storage_folder / f"{str(item_id)}_camera_#2.jpg").open("wb") as f2,
        ):
            f1.write(expected_picture)
            f2.write(expected_picture)
        expected_binary_names = [f"{str(item_id)}_camera_#1.jpg", f"{str(item_id)}_camera_#2.jpg"]

        # When
        actual_binary_names = binary_storage.get_item_binary_names(item_id)

        # Then
        assert len(actual_binary_names) == 2
        for i, actual_binary in enumerate(sorted(actual_binary_names)):
            assert actual_binary == expected_binary_names[i]

    def test_get_item_binary_should_return_requested_binary(self, tmp_path: Path, station_config: StationConfig):
        # Given
        target_directory = tmp_path / "binaries"
        target_directory.mkdir()
        station_config.binary_storage_config.target_directory = target_directory
        storing_path_manager = StoringPathManager(station_config.binary_storage_config, station_config.station_name)
        binary_storage = FileSystemBinaryStorage(station_config, storing_path_manager)

        expected_picture = bytes([0, 1, 2, 3, 4])
        item_id = UUID("00000000-0000-0000-0000-000000000001")
        item_storage_folder = target_directory / station_config.station_name
        item_storage_folder.mkdir(parents=True)
        with (item_storage_folder / f"{str(item_id)}_camera_#1.jpg").open("wb") as f:
            f.write(expected_picture)

        # When
        actual_binary = binary_storage.get_item_binary(item_id, "camera_#1")

        # Then
        assert actual_binary == expected_picture
