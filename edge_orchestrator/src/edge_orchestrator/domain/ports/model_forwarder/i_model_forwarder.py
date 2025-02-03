from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict, List

import numpy as np

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction


class IModelForwarder(ABC):
    _logger: Logger
    _model_forwarder_config: ModelForwarderConfig

    async def predict_on_binary(self, binary: bytes) -> Prediction:
        self._logger.info("Preprocessing binary")
        preprocessed_binary = self._pre_process_binary(binary)
        self._logger.info(f"Getting prediction from: {self._get_model_url()}")
        prediction_response = await self._predict(preprocessed_binary)
        self._logger.info("Post processing prediction")
        return self._post_process_prediction(prediction_response)

    @abstractmethod
    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        pass

    @abstractmethod
    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        pass

    def _get_model_url(self) -> str:
        base_url = self._model_forwarder_config.model_serving_url
        model_name = self._model_forwarder_config.model_name
        model_version = self._model_forwarder_config.model_version
        return f"{base_url}v1/models/{model_name}/versions/{model_version}:predict"

    def _get_class_names(self) -> List[str]:
        if self._model_forwarder_config.class_names:
            return self._model_forwarder_config.class_names
        else:
            with self._model_forwarder_config.class_names_filepath.open() as f:
                return [c.strip() for c in f.readlines()]
