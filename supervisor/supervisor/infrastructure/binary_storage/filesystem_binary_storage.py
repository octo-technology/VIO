from pathlib import Path
from typing import List

from supervisor.domain.models.item import Item
from supervisor.domain.ports.binary_storage import BinaryStorage


class FileSystemBinaryStorage(BinaryStorage):

    def __init__(self, src_directory_path: Path):
        self.folder = src_directory_path

    def save_item_binaries(self, item: Item):
        path = self.folder / item.id
        path.mkdir(parents=True, exist_ok=True)
        for camera_id, binary in item.binaries.items():
            filepath = _get_filepath(self.folder, item.id, camera_id)
            with filepath.open('wb') as f:
                f.write(binary)

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        filepath = _get_filepath(self.folder, item_id, camera_id)
        with filepath.open('rb') as f:
            return f.read()

    def get_item_binaries(self, item_id: str) -> List[str]:
        filepath = self.folder / item_id
        return [binary_path.name for binary_path in filepath.glob('*')]


def _get_filepath(folder: Path, item_id: str, camera_id: str) -> Path:
    return folder / item_id / (camera_id + '.jpg')
