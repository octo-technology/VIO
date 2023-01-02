from typing import Dict, Union

from abc import ABC, abstractmethod
from edge_orchestrator.domain.models.decision import Decision


class CameraRule(ABC):

    @abstractmethod
    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        pass
