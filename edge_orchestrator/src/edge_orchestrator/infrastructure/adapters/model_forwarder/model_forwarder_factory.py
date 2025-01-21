import logging

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
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
        if model_forwarder_config.model_type == ModelType.FAKE.value:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
                FakeModelForwarder,
            )

            return FakeModelForwarder(model_forwarder_config)

        elif model_forwarder_config.model_type == ModelType.CLASSIFICATION.value:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.classif_model_forwarder import (
                ClassifModelForwarder,
            )

            return ClassifModelForwarder(model_forwarder_config)

        elif model_forwarder_config.model_type == ModelType.OBJECT_DETECTION.value:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.detection_model_forwarder import (
                DetectionModelForwarder,
            )

            return DetectionModelForwarder(model_forwarder_config)

        elif model_forwarder_config.model_type == ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION.value:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.detection_with_classif_model_forwarder import (
                DetectionWithClassifModelForwarder,
            )

            return DetectionWithClassifModelForwarder(model_forwarder_config)

        else:
            raise ValueError(f"Model type ({model_forwarder_config.model_type}) is not supported.")
