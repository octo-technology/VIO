from supervisor import logger
from supervisor.domain.models.model_infos import ModelInfos, ModelTypes
from supervisor.domain.ports.model_forward import ModelForward
from supervisor.infrastructure.model_forward.tf_serving_classification_wrapper import (
    TFServingClassificationWrapper,
)
from supervisor.infrastructure.model_forward.tf_serving_detection_and_classification_wrapper import \
    TFServingDetectionClassificationWrapper
from supervisor.infrastructure.model_forward.tf_serving_detection_wrapper import (
    TFServingDetectionWrapper,
)


class TFServingWrapper(ModelForward):
    def __init__(self, serving_model_url, inventory, station_config):
        self.serving_model_url = serving_model_url
        self.inventory = inventory
        self.station_config = station_config

    async def perform_inference(self,
                                model: ModelInfos,
                                binary_data: bytes,
                                binary_name: str) -> dict:
        if model.category == ModelTypes.CLASSIFICATION.value:
            return await TFServingClassificationWrapper(self.serving_model_url) \
                .perform_inference(model, binary_data, binary_name)
        elif model.category == ModelTypes.OBJECT_DETECTION.value:
            return await TFServingDetectionWrapper(self.serving_model_url, model.class_names_path) \
                .perform_inference(model, binary_data, binary_name)
        elif model.category == ModelTypes.OBJECT_DETECTION_WITH_CLASSIFICATION.value:
            return await TFServingDetectionClassificationWrapper(self.serving_model_url, model.class_names_path)\
                .perform_inference(model, binary_data, binary_name)
        else:
            logger.error(
                f"Enter a valid model category, model category entered and invalid : {model.category}"
            )
