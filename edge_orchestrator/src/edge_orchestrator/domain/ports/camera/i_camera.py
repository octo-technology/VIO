from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Image


class ICamera(ABC):
    _logger: Logger
    _camera_config: CameraConfig

    @abstractmethod
    def capture(self) -> Image:
        pass

    @abstractmethod
    def release(self):
        pass
