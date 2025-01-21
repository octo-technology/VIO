from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class ICameraFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_camera(self, camera_config: CameraConfig) -> ICamera:
        pass
