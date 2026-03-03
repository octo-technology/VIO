import logging

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_factory import (
    IModelForwarderFactory,
)


class ModelForwarderFactory(IModelForwarderFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_model_forwarder(self, model_forwarder_config: ModelForwarderConfig) -> IModelForwarder:
        if model_forwarder_config.model_name == "fake_model":
            from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
                FakeModelForwarder,
            )

            return FakeModelForwarder(model_forwarder_config)

        from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder import (
            ModelForwarder,
        )

        return ModelForwarder(model_forwarder_config)
