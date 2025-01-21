import logging
import subprocess
from pathlib import Path

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class UsbCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)

    def capture(self) -> bytes:
        resolution = "640x640"
        source = self.settings["source"]
        img_save_path = f"{source}.jpg".replace("/", "")
        cmd = f"fswebcam -r {resolution} -S 3 --jpeg 50 --save {img_save_path} -d {source}"
        cmd_feedback = subprocess.run([cmd], shell=True)
        self._logger.info(f"Camera exit code: {cmd_feedback.returncode}")
        return Path(img_save_path).open("rb").read()

    def get_camera_config(self) -> CameraConfig:
        return self._camera_config
