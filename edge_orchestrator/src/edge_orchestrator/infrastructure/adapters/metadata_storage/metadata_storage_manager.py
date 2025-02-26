import logging

from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage import (
    IMetadataStorage,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)


class MetadataStorageManager(IMetadataStorageManager):
    def __init__(self, metadata_storage_factory: IMetadataStorageFactory):
        self._metadata_storage_factory = metadata_storage_factory
        self._metadata_storages = {}
        self._logger = logging.getLogger(__name__)

    def get_metadata_storage(self, station_config: StationConfig) -> IMetadataStorage:
        metadata_storage_type = station_config.metadata_storage_config.storage_type
        if metadata_storage_type not in self._metadata_storages or station_config.metadata_storage_config.recreate_me:
            metadata_storage = self._metadata_storage_factory.create_metadata_storage(station_config)
            self._metadata_storages[metadata_storage_type] = metadata_storage
        return self._metadata_storages[metadata_storage_type]
