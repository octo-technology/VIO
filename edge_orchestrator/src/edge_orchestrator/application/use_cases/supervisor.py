import logging

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
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
        station_config: StationConfig,
        metadata_storage_manager: IMetadataStorageManager,
        binary_storage_manager: IBinaryStorageManager,
        model_forwarder_manager: IModelForwarderManager,
        camera_rule_manager: ICameraRuleManager,
        item_rule_manager: IItemRuleManager,
        camera_manager: ICameraManager,
    ):
        self._logger = logging.getLogger(__name__)
        self._station_config = station_config
        self._metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
        self._binary_storage = binary_storage_manager.get_binary_storage(station_config)
        self._model_forwarder_manager = model_forwarder_manager
        self._camera_rule_manager = camera_rule_manager
        self._item_rule = item_rule_manager.get_item_rule(station_config.item_rule_config)
        self._camera_manager = camera_manager

    async def inspect(self, item: Item):
        self._logger.info("Taking pictures...")
        self._camera_manager.take_pictures(item)
        item.state = ItemState.CAPTURE

        self._logger.info("Saving pictures...")
        self._binary_storage.save_item_binaries(item)
        item.state = ItemState.SAVE_BINARIES

        self._logger.info("Predicting on pictures...")
        await self._model_forwarder_manager.predict_on_binaries(item)
        item.state = ItemState.INFERENCE

        self._logger.info("Applying rule on each picture...")
        self._camera_rule_manager.apply_camera_rules(item)
        item.state = ItemState.CAMERA_RULE

        self._logger.info("Applying rule on item...")
        self._item_rule.apply_item_rules(item)
        item.state = ItemState.ITEM_RULE

        self._logger.info("Saving item metadata...")
        item.state = ItemState.DONE
        self._metadata_storage.save_item_metadata(item)

        self._logger.info("Inspection done!")
