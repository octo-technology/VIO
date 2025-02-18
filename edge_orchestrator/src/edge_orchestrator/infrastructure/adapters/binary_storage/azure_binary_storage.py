import logging
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)


class AzureBinaryStorage(IBinaryStorage):
    def __init__(self, station_config: StationConfig):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)

    def save_item_binaries(self, item: Item):
        raise NotImplementedError("Not implemented yet")

    def get_item_binary_names(self, item_id: UUID) -> List[str]:
        raise NotImplementedError("Not implemented yet")

    def get_item_binaries(self, item_id: UUID) -> Dict[str, bytes]:
        raise NotImplementedError("Not implemented yet")

    def get_item_binary(self, item_id: UUID, camera_id: str) -> bytes:
        raise NotImplementedError("Not implemented yet")

    def _get_storing_path(self, item_id: UUID) -> Path:
        raise NotImplementedError("Not implemented yet")
