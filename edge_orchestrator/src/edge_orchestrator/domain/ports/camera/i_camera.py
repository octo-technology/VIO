from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig


class ICamera(ABC):
    _logger: Logger
    _camera_config: CameraConfig

    @abstractmethod
    def capture(self) -> bytes:
        pass

    @abstractmethod
    def get_camera_config(self) -> CameraConfig:
        pass
