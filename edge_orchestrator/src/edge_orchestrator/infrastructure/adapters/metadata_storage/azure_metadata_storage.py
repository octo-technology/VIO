import logging
from pathlib import Path
from typing import List
from uuid import UUID

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)


class AzureMetadataStorage(IMetadataStorage):
    def __init__(self, station_config: StationConfig):
        self._station_config: StationConfig = station_config
        self._logger = logging.getLogger(__name__)

    def save_item_metadata(self, item: Item):
        raise NotImplementedError("Not implemented yet")

    def get_item_metadata(self, item_id: UUID) -> Item:
        raise NotImplementedError("Not implemented yet")

    def get_all_items_metadata(self) -> List[Item]:
        raise NotImplementedError("Not implemented yet")

    def _get_storing_path(self, item_id: UUID) -> Path:
        raise NotImplementedError("Not implemented yet")
