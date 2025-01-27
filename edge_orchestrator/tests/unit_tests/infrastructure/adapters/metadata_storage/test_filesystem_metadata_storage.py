import json
from pathlib import Path
from uuid import UUID

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.infrastructure.adapters.metadata_storage.filesystem_metadata_storage import (
    FileSystemMetadataStorage,
)


class TestFileSystemMetadataStorage:
    def test_save_item_metadata_with_empty_item_should_write_metadata_on_filesystem(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        metadata_storage = FileSystemMetadataStorage(storage_config)
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
        path_to_metadata = target_directory / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata

    def test_save_item_metadata_should_write_metadata_on_filesystem(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        metadata_storage = FileSystemMetadataStorage(storage_config)
        item_id = UUID("00000000-0000-0000-0000-000000000002")

        item = Item(
            id=item_id,
            cameras_metadata={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.FAKE),
                "camera_#2": CameraConfig(camera_id="camera_#2", camera_type=CameraType.USB),
            },
            binaries={"camera_#1": bytes([0, 1, 2, 3, 4]), "camera_#2": bytes([0, 1, 2, 3, 4])},
            predictions={
                "camera#1": ClassifPrediction(
                    prediction_type=ModelType.CLASSIFICATION, label=Decision.OK, probability=0.41
                ),
                "camera#2": ClassifPrediction(
                    prediction_type=ModelType.CLASSIFICATION, label=Decision.OK, probability=0.96
                ),
            },
            camera_decisions={"camera#1": Decision.OK, "camera#2": Decision.OK},
            decision=Decision.OK,
        )

        expected_metadata = {
            "id": "00000000-0000-0000-0000-000000000002",
            "cameras_metadata": {
                "camera_#1": {
                    "camera_id": "camera_#1",
                    "camera_type": "fake",
                    "source_directory": None,
                    "position": "front",
                    "model_forwarder_config": None,
                    "camera_rule_config": None,
                },
                "camera_#2": {
                    "camera_id": "camera_#2",
                    "camera_type": "usb",
                    "source_directory": None,
                    "position": "front",
                    "model_forwarder_config": None,
                    "camera_rule_config": None,
                },
            },
            "predictions": {
                "camera#1": {"prediction_type": "classification", "label": "OK", "probability": 0.41},
                "camera#2": {"prediction_type": "classification", "label": "OK", "probability": 0.96},
            },
            "camera_decisions": {"camera#1": "OK", "camera#2": "OK"},
            "decision": "OK",
        }

        # When
        metadata_storage.save_item_metadata(item)

        # Then
        path_to_metadata = target_directory / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata == expected_metadata

    def test_save_item_metadata_with_prefix_should_write_metadata_on_filesystem(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        prefix = "station_#1"
        storage_config = StorageConfig(target_directory=target_directory, prefix=prefix)
        metadata_storage = FileSystemMetadataStorage(storage_config)
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
        path_to_metadata = target_directory / prefix / f"{str(item.id)}.json"
        assert path_to_metadata.is_file()
        actual_metadata = json.load(path_to_metadata.open("r"))
        assert actual_metadata

    def test_get_item_metadata_should_return_requested_item_metadata(self, tmp_path: Path):
        # Given
        target_directory = tmp_path / "metadata"
        target_directory.mkdir()
        storage_config = StorageConfig(target_directory=target_directory)
        metadata_storage = FileSystemMetadataStorage(storage_config)
        item_id = UUID("00000000-0000-0000-0000-000000000003")

        expected_metadata = {
            "id": "00000000-0000-0000-0000-000000000003",
            "cameras_metadata": {
                "camera_#1": {"camera_id": "camera_#1", "camera_type": "fake"},
                "camera_#2": {"camera_id": "camera_#2", "camera_type": "usb"},
            },
            "predictions": {
                "camera#1": {"prediction_type": "classification", "label": "OK", "probability": 0.41},
                "camera#2": {"prediction_type": "classification", "label": "OK", "probability": 0.96},
            },
            "camera_decisions": {"camera#1": "OK", "camera#2": "OK"},
            "decision": "OK",
        }

        with (target_directory / f"{item_id}.json").open("w") as f:
            json.dump(expected_metadata, f)

        # When
        actual_metadata = metadata_storage.get_item_metadata(item_id)

        # Then
        assert actual_metadata == expected_metadata
