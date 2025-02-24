import logging

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_manager import (
    ICameraRuleManager,
)
from edge_orchestrator.domain.ports.item_rule.i_item_rule_manager import (
    IItemRuleManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_manager import (
    IModelForwarderManager,
)
from edge_orchestrator.utils.singleton import SingletonMeta


class Supervisor(metaclass=SingletonMeta):
    def __init__(
        self,
        metadata_storage_manager: IMetadataStorageManager,
        binary_storage_manager: IBinaryStorageManager,
        model_forwarder_manager: IModelForwarderManager,
        camera_rule_manager: ICameraRuleManager,
        item_rule_manager: IItemRuleManager,
        camera_manager: ICameraManager,
    ):
        self._logger = logging.getLogger(__name__)
        self._metadata_storage_manager = metadata_storage_manager
        self._binary_storage_manager = binary_storage_manager
        self._model_forwarder_manager = model_forwarder_manager
        self._camera_rule_manager = camera_rule_manager
        self._item_rule_manager = item_rule_manager
        self._camera_manager = camera_manager

    async def inspect(self, item: Item, station_config: StationConfig):
        self._camera_manager.take_pictures(item)

        self._binary_storage_manager.get_binary_storage(station_config).save_item_binaries(item)

        await self._model_forwarder_manager.predict_on_binaries(item)

        self._camera_rule_manager.apply_camera_rules(item)

        self._item_rule_manager.get_item_rule(station_config.item_rule_config).apply_item_rules(item)

        self._metadata_storage_manager.get_metadata_storage(station_config).save_item_metadata(item)
