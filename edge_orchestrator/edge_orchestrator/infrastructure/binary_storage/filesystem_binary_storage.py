from pathlib import Path
from typing import List, Optional

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage
from edge_orchestrator.infrastructure.filesystem_helpers import get_tmp_path


class FileSystemBinaryStorage(BinaryStorage):
    def __init__(self, src_directory: Optional[str] = None):
        if src_directory is None:
            self.folder = get_tmp_path()
        else:
            self.folder = Path(src_directory)

    def save_item_binaries(self, item: Item):
        path = self.folder / item.id
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, binary in item.binaries.items():
            filepath = _get_filepath(self.folder, item.id, camera_id)
            with filepath.open("wb") as f:
                f.write(binary)

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filepath = _get_filepath(self.folder, item_id, camera_id)
        with filepath.open("rb") as f:
            return f.read()

    def get_item_binaries(self, item_id: str) -> List[str]:
        filepath = self.folder / item_id
        return [binary_path.name for binary_path in filepath.glob("*")]


def _get_filepath(folder: Path, item_id: str, camera_id: str) -> Path:
    return folder / item_id / (camera_id + ".jpg")
