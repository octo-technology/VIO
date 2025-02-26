import logging

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
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
        if model_forwarder_config.model_name == ModelName.fake_model:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
                FakeModelForwarder,
            )

            return FakeModelForwarder(model_forwarder_config)
        elif model_forwarder_config.model_type == ModelType.classification:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.classif_model_forwarder import (
                ClassifModelForwarder,
            )

            return ClassifModelForwarder(model_forwarder_config)

        elif model_forwarder_config.model_type == ModelType.object_detection:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.object_detection_model_forwarder import (
                ObjectDetectionModelForwarder,
            )

            return ObjectDetectionModelForwarder(model_forwarder_config)

        elif model_forwarder_config.model_type == ModelType.segmentation:
            from edge_orchestrator.infrastructure.adapters.model_forwarder.segmentation_model_forwarder import (
                SegmentationModelForwarder,
            )

            return SegmentationModelForwarder(model_forwarder_config)
        else:
            raise ValueError(f"Model type ({model_forwarder_config.model_type}) is not supported.")
