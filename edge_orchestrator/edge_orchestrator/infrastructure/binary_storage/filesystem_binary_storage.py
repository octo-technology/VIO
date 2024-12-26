from pathlib import Path
from typing import List

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


class FileSystemBinaryStorage(BinaryStorage):
    def __init__(self, src_directory_path: Path, active_config_name: str):
        self.active_config_name = active_config_name
        self.folder = src_directory_path

    def save_item_binaries(self, item: Item):
        path = self.folder / self.active_config_name / item.id
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, binary in item.binaries.items():
            filepath = _get_filepath(self.folder, item.id, camera_id, self.active_config_name)
            with filepath.open("wb") as f:
                f.write(binary)

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filepath = _get_filepath(self.folder, item_id, camera_id, self.active_config_name)
        with filepath.open("rb") as f:
            return f.read()

    def get_item_binaries(self, item_id: str) -> List[str]:
        filepath = self.folder / self.active_config_name / item_id
        return [binary_path.name for binary_path in filepath.glob("*")]

    def get_item_binary_filepath(self, item_id: str, camera_id: str) -> str:
        return str(_get_filepath(self.folder, item_id, camera_id, self.active_config_name))


def _get_filepath(folder: Path, item_id: str, camera_id: str, active_config_name: str) -> Path:
    return folder / active_config_name / item_id / (camera_id + ".jpg")
