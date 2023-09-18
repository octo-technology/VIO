from functools import lru_cache
from typing import Dict, Type, Optional, Any

from edge_orchestrator.domain.ports.model_forward import ModelForward
from edge_orchestrator.infrastructure.model_forward.fake_model_forward import (
    FakeModelForward,
)
from edge_orchestrator.infrastructure.model_forward.tf_serving_wrapper import (
    TFServingWrapper,
)

AVAILABLE_MODEL_FORWARD: Dict[str, Type[ModelForward]] = {
    "fake": FakeModelForward,
    "tf_serving": TFServingWrapper,
}


class ModelForwardFactory:
    @staticmethod
    @lru_cache()
    def get_model_forward(
        model_forward_type: Optional[str] = "fake",
        **model_forward_params: Optional[Dict[str, Any]],
    ) -> ModelForward:
        try:
            return AVAILABLE_MODEL_FORWARD[model_forward_type](**model_forward_params)
        except KeyError as err:
            raise ValueError(
                f"Unknown model forward type: {model_forward_type}"
            ) from err
