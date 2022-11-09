from typing import Dict, Union

from abc import ABC, abstractmethod
from supervisor.domain.models.decision import Decision


class CameraRule(ABC):

    @abstractmethod
    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        pass
