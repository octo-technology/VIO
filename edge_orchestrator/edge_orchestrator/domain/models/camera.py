from abc import ABC, abstractmethod
from typing import Dict, Union


def get_last_inference_by_camera(inference: Dict) -> Dict:
    last_model = list(inference.keys())[len(inference) - 1]
    last_model_inference = inference[last_model]
    return last_model_inference


class Camera(ABC):
    id: str
    settings: Dict[str, Union[str, Dict]]

    @abstractmethod
    def capture(self) -> bytes:
        pass

    @abstractmethod
    def apply_settings(self, settings: Dict):
        pass
