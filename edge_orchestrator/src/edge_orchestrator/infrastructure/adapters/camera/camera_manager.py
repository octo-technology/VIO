import logging
from typing import Dict

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.domain.ports.camera.i_camera_factory import ICameraFactory
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager


class NoCameraAvailableError(Exception):
    pass


class CameraManager(ICameraManager):
    def __init__(self, camera_factory: ICameraFactory):
        self._camera_factory = camera_factory
        self._cameras: Dict[str, ICamera] = {}
        self._logger = logging.getLogger(__name__)

    def create_cameras(self, station_config: StationConfig):
        for camera_id, camera_config in station_config.camera_configs.items():
            if camera_id not in self._cameras:
                camera = self._camera_factory.create_camera(camera_config)
                self._cameras[camera_id] = camera

    def take_pictures(self, item: Item):
        if self._cameras is None or len(self._cameras) == 0:
            raise NoCameraAvailableError("No camera available to take picture!")

        binaries: Dict[str, bytes] = {}
        cameras_metadata: Dict[str, CameraConfig] = {}
        for camera_id, camera in self._cameras.items():
            binaries[camera_id] = camera.capture()
            cameras_metadata[camera_id] = camera.get_camera_config()
        item.binaries = binaries
        item.cameras_metadata = cameras_metadata
