import logging
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_factory import (
    IModelForwarderFactory,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_manager import (
    IModelForwarderManager,
)


class ModelForwarderManager(IModelForwarderManager):
    def __init__(self, model_forwarder_factory: IModelForwarderFactory):
        self._model_forwarder_factory = model_forwarder_factory
        self._model_forwarders: Dict[str, IModelForwarder] = {}
        self._logger = logging.getLogger(__name__)

    def _get_model_forwarder(self, model_forwarder_config: ModelForwarderConfig) -> IModelForwarder:
        model_id = model_forwarder_config.model_id
        if model_id not in self._model_forwarders or model_forwarder_config.recreate_me:
            self._logger.info(f"Creating model forwarder for model_id: {model_id}")
            model_forwarder = self._model_forwarder_factory.create_model_forwarder(model_forwarder_config)
            self._model_forwarders[model_id] = model_forwarder
        return self._model_forwarders[model_id]

    async def predict_on_binaries(self, item: Item):
        if len(self._model_forwarders) == 0:
            self._logger.warning(
                "No model forwarder available to predict on item pictures! May take some extra time to instantiate."
            )

        for camera_id, camera_config in item.cameras_metadata.items():
            model_forwarder_config: ModelForwarderConfig = camera_config.model_forwarder_config
            model_forwarder = self._get_model_forwarder(model_forwarder_config)
            if camera_id not in item.binaries or item.binaries[camera_id].image_bytes is None:
                self._logger.warning(f"Camera {camera_id} has no image bytes to predict on.")
            else:
                item.predictions[camera_id] = await model_forwarder.predict_on_binary(
                    item.binaries[camera_id].image_bytes
                )
