import logging
from typing import Dict

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.domain.ports.camera.i_camera_factory import ICameraFactory
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager


class CameraManager(ICameraManager):
    def __init__(self, camera_factory: ICameraFactory):
        self._camera_factory = camera_factory
        self._cameras: Dict[str, ICamera] = {}
        self._logger = logging.getLogger(__name__)
        self._camera_configs: Dict[str, CameraConfig] = {}

    def create_cameras(self, station_config: StationConfig):
        self._camera_configs = station_config.camera_configs
        for camera_id, camera_config in station_config.camera_configs.items():
            if camera_id in self._cameras:
                self._logger.info(f"Camera {camera_id} already exists, skipping creation...")
                continue
            else:
                self._logger.info(f"Creating camera {camera_id}")
                try:
                    camera = self._camera_factory.create_camera(camera_config)
                    self._cameras[camera_id] = camera
                except Exception:
                    pass
                self._logger.info(f"Camera {camera_id} created!")

    def take_pictures(self, item: Item):
        self._logger.info("Taking pictures...")

        if self._cameras is None or len(self._cameras) == 0:
            self._logger.error("No camera available to take picture!")
            return

        binaries: Dict[str, bytes] = {}
        cameras_metadata: Dict[str, CameraConfig] = {}
        for camera_id, camera_config in self._camera_configs.items():
            cameras_metadata[camera_id] = camera_config
            try:
                binaries[camera_id] = self._cameras[camera_id].capture()
                self._logger.info(f"Image captured from camera {camera_id}!")
            except Exception:
                self._logger.exception(f"Error while capturing image from camera {camera_id}")
                continue
        item.binaries = binaries
        item.cameras_metadata = cameras_metadata
        item.state = ItemState.CAPTURE

    def reset(self):
        for camera_id, camera in self._cameras.items():
            try:
                camera.release()
            except Exception:
                self._logger.exception(f"Error while releasing camera {camera_id}")
        self._cameras = {}
        self._camera_configs = {}
