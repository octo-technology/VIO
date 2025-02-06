import logging

from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage import (
    IBinaryStorage,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)


class BinaryStorageManager(IBinaryStorageManager):
    def __init__(self, binary_storage_factory: IBinaryStorageFactory):
        self._binary_storage_factory = binary_storage_factory
        self._binary_storages = {}
        self._logger = logging.getLogger(__name__)

    def get_binary_storage(self, binary_storage_config: StorageConfig) -> IBinaryStorage:
        binary_storage_type = binary_storage_config.storage_type
        if binary_storage_type not in self._binary_storages or binary_storage_config.recreate_me:
            binary_storage = self._binary_storage_factory.create_binary_storage(binary_storage_config)
            self._binary_storages[binary_storage_type] = binary_storage
        return self._binary_storages[binary_storage_type]
