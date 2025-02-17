import json
from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.infrastructure.adapters.metadata_storage.filesystem_metadata_storage import (
    FileSystemMetadataStorage,
)


class TestFileSystemMetadataStorage:
    def test_save_item_metadata_with_empty_item_should_write_metadata_on_filesystem(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        station_config.metadata_storage_config.target_directory = target_directory
        metadata_storage = FileSystemMetadataStorage(station_config)
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
        )
        actual_metadata = {
            "id": "00000000-0000-0000-0000-000000000001",
            "cameras_metadata": {},
            "predictions": {},
            "camera_decisions": {},
            "decision": None,
        }

        # When
        metadata_storage.save_item_metadata(item)

        # Then
        path_to_metadata = target_directory / station_config.station_name / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata

    def test_save_item_metadata_should_write_metadata_on_filesystem(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        station_config.metadata_storage_config.target_directory = target_directory
        metadata_storage = FileSystemMetadataStorage(station_config)
        item_id = UUID("00000000-0000-0000-0000-000000000002")

        item = Item(
            id=item_id,
            creation_date="2025-02-04T09:23:10.437614",
            cameras_metadata={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.FAKE, source_directory="fake"),
                "camera_#2": CameraConfig(camera_id="camera_#2", camera_type=CameraType.USB, source_directory="fake"),
            },
            binaries={
                "camera_#1": Image(
                    creation_date="2025-02-04T12:05:39.744489",
                    storing_path=Path("/fake/path/image_1.jpg"),
                    image_bytes=bytes(
                        [0, 1, 2, 3, 4],
                    ),
                ),
                "camera_#2": Image(
                    creation_date="2025-02-04T12:05:42.245863",
                    storing_path=Path("/fake/path/image_2.jpg"),
                    image_bytes=bytes(
                        [0, 1, 2, 3, 4],
                    ),
                ),
            },
            predictions={
                "camera_#1": ClassifPrediction(prediction_type=PredictionType.class_, label="OK", probability=0.41),
                "camera_#2": ClassifPrediction(prediction_type=PredictionType.class_, label="OK", probability=0.96),
            },
            camera_decisions={"camera_#1": Decision.OK, "camera_#2": Decision.OK},
            decision=Decision.OK,
            state=ItemState.DONE,
        )

        expected_metadata = {
            "id": "00000000-0000-0000-0000-000000000002",
            "creation_date": "2025-02-04T09:23:10.437614",
            "cameras_metadata": {
                "camera_#1": {
                    "camera_id": "camera_#1",
                    "camera_type": "fake",
                    "position": "front",
                    "source_directory": "fake",
                    "recreate_me": False,
                },
                "camera_#2": {
                    "camera_id": "camera_#2",
                    "camera_type": "usb",
                    "position": "front",
                    "source_directory": "fake",
                    "recreate_me": False,
                },
            },
            "binaries": {
                "camera_#1": {"creation_date": "2025-02-04T12:05:39.744489", "storing_path": "/fake/path/image_1.jpg"},
                "camera_#2": {"creation_date": "2025-02-04T12:05:42.245863", "storing_path": "/fake/path/image_2.jpg"},
            },
            "predictions": {
                "camera_#1": {"prediction_type": "class", "label": "OK", "probability": 0.41},
                "camera_#2": {"prediction_type": "class", "label": "OK", "probability": 0.96},
            },
            "camera_decisions": {"camera_#1": "OK", "camera_#2": "OK"},
            "decision": "OK",
            "state": "DONE",
        }

        # When
        metadata_storage.save_item_metadata(item)

        # Then
        path_to_metadata = target_directory / station_config.station_name / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata == expected_metadata

    def test_save_item_metadata_with_prefix_should_write_metadata_on_filesystem(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        prefix = "station_#1"
        station_config.metadata_storage_config.target_directory = target_directory
        station_config.metadata_storage_config.prefix = prefix
        metadata_storage = FileSystemMetadataStorage(station_config)
        item_id = UUID("00000000-0000-0000-0000-000000000001")

        item = Item(
            id=item_id,
        )
        actual_metadata = {
            "id": "00000000-0000-0000-0000-000000000001",
            "cameras_metadata": {},
            "binaries": {},
            "predictions": {},
            "camera_decisions": {},
            "decision": None,
        }

        # When
        metadata_storage.save_item_metadata(item)

        # Then
        path_to_metadata = target_directory / station_config.station_name / prefix / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata

    def test_get_item_metadata_should_return_requested_item_metadata(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        station_config.metadata_storage_config.target_directory = target_directory
        metadata_storage = FileSystemMetadataStorage(station_config)
        item_id = UUID("00000000-0000-0000-0000-000000000003")

        expected_metadata = {
            "id": "00000000-0000-0000-0000-000000000003",
            "creation_date": "2025-02-04T09:18:09.433619",
            "cameras_metadata": {
                "camera_#1": {
                    "camera_id": "camera_#1",
                    "camera_type": "fake",
                    "source_directory": "fake",
                    "reacreate_me": False,
                },
                "camera_#2": {
                    "camera_id": "camera_#2",
                    "camera_type": "usb",
                    "source_directory": "fake",
                    "reacreate_me": False,
                },
            },
            "binaries": {
                "camera_#1": {"creation_date": "2025-02-04T12:05:39.744489", "storing_path": "/fake/path/image_1.jpg"},
                "camera_#2": {"creation_date": "2025-02-04T12:05:42.245863", "storing_path": "/fake/path/image_2.jpg"},
            },
            "predictions": {
                "camera_#1": {"prediction_type": "class", "label": "OK", "probability": 0.41},
                "camera_#2": {"prediction_type": "class", "label": "OK", "probability": 0.96},
            },
            "camera_decisions": {"camera_#1": "OK", "camera_#2": "OK"},
            "decision": "OK",
            "state": "DONE",
        }

        (target_directory / station_config.station_name).mkdir(parents=True)
        with (target_directory / station_config.station_name / f"{item_id}.json").open("w") as f:
            json.dump(expected_metadata, f)

        # When
        actual_item_metadata = metadata_storage.get_item_metadata(item_id)

        # Then
        assert actual_item_metadata == Item(**expected_metadata)

    def test_get_all_items_metadata_should_return_requested_metadata(
        self, tmp_path: Path, station_config: StationConfig
    ):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        station_config.metadata_storage_config.target_directory = target_directory
        metadata_storage = FileSystemMetadataStorage(station_config)

        for i in range(5):
            uid = f"00000000-0000-0000-0000-00000000000{i+1}"
            expected_metadata = {
                "id": uid,
                "creation_date": "2025-02-04T09:18:09.433619",
                "cameras_metadata": {
                    "camera_#1": {
                        "camera_id": "camera_#1",
                        "camera_type": "fake",
                        "source_directory": "fake",
                        "reacreate_me": False,
                    },
                    "camera_#2": {
                        "camera_id": "camera_#2",
                        "camera_type": "usb",
                        "source_directory": "fake",
                        "reacreate_me": False,
                    },
                },
                "binaries": {
                    "camera_#1": {
                        "creation_date": "2025-02-04T12:05:39.744489",
                        "storing_path": "/fake/path/image_1.jpg",
                    },
                    "camera_#2": {
                        "creation_date": "2025-02-04T12:05:42.245863",
                        "storing_path": "/fake/path/image_2.jpg",
                    },
                },
                "predictions": {
                    "camera_#1": {"prediction_type": "class", "label": "OK", "probability": 0.41},
                    "camera_#2": {"prediction_type": "class", "label": "OK", "probability": 0.96},
                },
                "camera_decisions": {"camera_#1": "OK", "camera_#2": "OK"},
                "decision": "OK",
                "state": "DONE",
            }

            (target_directory / station_config.station_name).mkdir(parents=True, exist_ok=True)
            with (target_directory / station_config.station_name / f"{uid}.json").open("w") as f:
                json.dump(expected_metadata, f)

        # When
        actual_items_metadata = metadata_storage.get_all_items_metadata()

        # Then
        assert len(actual_items_metadata) == 5
        actual_items_metadata = sorted(actual_items_metadata, key=lambda metadata: metadata.id)
        assert actual_items_metadata[4] == Item(**expected_metadata)
