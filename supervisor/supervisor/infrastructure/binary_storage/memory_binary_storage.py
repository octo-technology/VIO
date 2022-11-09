from typing import List

from supervisor.domain.models.item import Item
from supervisor.domain.ports.binary_storage import BinaryStorage


class MemoryBinaryStorage(BinaryStorage):

    def __init__(self):
        self.binaries = {}

    def save_item_binaries(self, item: Item) -> None:
        binaries_dict = {}
        for camera_id, binary in item.binaries.items():
            binaries_dict[camera_id] = binary
        self.binaries[item.id] = binaries_dict

    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        return self.binaries[item_id][camera_id]

    def get_item_binaries(self, item_id: str) -> List[str]:
        return list(self.binaries[item_id].keys())
