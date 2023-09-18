from typing import Dict, Tuple, Any, List

from application.dto.station_config import StationConfig
from domain.models.camera import Camera


class EdgeStation:
    def __init__(self, station_config: StationConfig):
        self.station_config = station_config
        self.cameras = self.register_cameras()

    def register_cameras(self) -> List[Camera]:
        cameras = []
        for camera_id in self.station_config.get_cameras():
            camera_type = self.station_config.get_camera_type(camera_id)
            camera_settings = self.station_config.get_camera_settings(camera_id)
            camera = camera_type(id=camera_id, settings=camera_settings)
            cameras.append(camera)
        return cameras

    def capture(self) -> Tuple[Dict, Dict]:
        binaries: Dict[str, bytes] = {}
        for camera in self.cameras:
            binaries[camera.id] = camera.capture()
        cameras_metadata: Dict[str, Any] = {
            camera.id: self.station_config.get_camera_settings(camera.id)
            for camera in self.cameras
        }
        return cameras_metadata, binaries
