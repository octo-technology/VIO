from abc import abstractmethod
from typing import List

from supervisor.domain.models.item import Item


class BinaryStorage:

    @abstractmethod
    def save_item_binaries(self, item: Item):
        pass

    @abstractmethod
    def get_item_binary(self, item_id: str, camera_id: str) -> bytes:
        pass

    @abstractmethod
    def get_item_binaries(self, item_id: str) -> List[str]:
        pass
