import logging

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.utils.singleton import SingletonMeta


class DataGathering(metaclass=SingletonMeta):
    def __init__(
        self,
        metadata_storage_manager: IMetadataStorageManager,
        binary_storage_manager: IBinaryStorageManager,
        camera_manager: ICameraManager,
    ):
        self._logger = logging.getLogger(__name__)
        self._metadata_storage_manager = metadata_storage_manager
        self._binary_storage_manager = binary_storage_manager
        self._camera_manager = camera_manager

    async def acquire(self, item: Item, station_config: StationConfig):
        self._camera_manager.create_cameras(station_config)
        self._camera_manager.take_pictures(item)

        self._binary_storage_manager.get_binary_storage(station_config).save_item_binaries(item)

        self._metadata_storage_manager.get_metadata_storage(station_config).save_item_metadata(item)

    async def upload(self, item: Item, station_config: StationConfig):
        self._binary_storage_manager.get_binary_storage(station_config).save_item_binaries(item)

        self._metadata_storage_manager.get_metadata_storage(station_config).save_item_metadata(item)

    def reset_managers(
        self, binary_storage_factory: IBinaryStorageFactory, metadata_storage_factory: IMetadataStorageFactory
    ):
        self._logger.info("Resetting all managers after configuration update...")
        self._metadata_storage_manager.reset(metadata_storage_factory)
        self._binary_storage_manager.reset(binary_storage_factory)
        self._camera_manager.reset()
        self._logger.info("Managers reset done!")
