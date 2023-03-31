from pathlib import Path
from typing import Tuple, Dict

from edge_orchestrator.domain.ports.station_config import StationConfig


class EdgeStation:

    def __init__(self, station_config: StationConfig, storage: Path):
        self.station_config = station_config
        self.storage = storage

    def register_cameras(self, station_config: StationConfig):
        self.cameras = []
        for camera_id in station_config.get_cameras():
            camera_type = station_config.get_camera_type(camera_id)
            camera_settings = station_config.get_camera_settings(camera_id)
            camera = camera_type(id=camera_id, settings=camera_settings)
            self.cameras.append(camera)

    def capture(self) -> Tuple[Dict, Dict]:
        binaries = {}
        for camera in self.cameras:
            binaries[camera.id] = camera.capture()
        cameras_metadata = {
            camera.id: self.station_config.get_camera_settings(camera.id) for camera in self.cameras
        }
        return cameras_metadata, binaries
