from pathlib import Path
from typing import List
from datetime import datetime

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
import uuid


def generate_id():
    return str(uuid.uuid4())


class FileSystemBinaryStorage(BinaryStorage):
    def __init__(self, src_directory_path: Path):
        self.folder = src_directory_path
        self.session_id = generate_id()

    def save_item_binaries(self, item: Item, active_config_name: str):
        path = (
            self.folder
            / (active_config_name + "_" + self.session_id)
            / datetime.today().strftime("%Y-%m-%d")
        )
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, binary in item.binaries.items():
            filepath = _get_filepath(
                self.folder, item.id, camera_id, active_config_name, self.session_id
            )
            with filepath.open("wb") as f:
                f.write(binary)

    def get_item_binary(
        self, item_id: str, camera_id: str, active_config_name: str
    ) -> bytes:
        filepath = _get_filepath(
            self.folder, item_id, camera_id, active_config_name, self.session_id
        )
        with filepath.open("rb") as f:
            return f.read()

    def get_item_binaries(self, item_id: str, active_config_name: str) -> List[str]:
        filepath = (
            self.folder
            / (active_config_name + "_" + self.session_id)
            / datetime.today().strftime("%Y-%m-%d")
        )
        return [binary_path.name for binary_path in filepath.glob("*")]


def _get_filepath(
    folder: Path, item_id: str, camera_id: str, active_config_name: str, session_id: str
) -> Path:
    return (
        folder
        / (active_config_name + "_" + session_id)
        / datetime.today().strftime("%Y-%m-%d")
        / (camera_id + "_" + item_id + ".jpg")
    )
