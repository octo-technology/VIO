from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.domain.ports.camera.i_camera_factory import ICameraFactory


class ICameraManager(ABC):
    _cameras: Dict[str, ICamera]
    _camera_factory: ICameraFactory
    _logger: Logger

    @abstractmethod
    def create_cameras(
        self,
        station_config: StationConfig,
    ):
        pass

    @abstractmethod
    def take_pictures(self, item: Item):
        pass
