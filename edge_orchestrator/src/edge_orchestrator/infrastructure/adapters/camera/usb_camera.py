import subprocess
import logging
from pathlib import Path

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.domain.models.image import Image

class UsbCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        self.src = self._camera_config.source_directory.as_posix()

    def capture(self) -> bytes:
        resolution = "640x640"
        img_save_path = f"{self.src}.jpg".replace("/", "")
        cmd = f"fswebcam -r {resolution} -S 3 --jpeg 50 --save {img_save_path} -d {self.src}"
        cmd_feedback = subprocess.run([cmd], shell=True)
        self._logger.info(f"Camera exit code: {cmd_feedback.returncode}")
        return Image(image_bytes=Path(img_save_path).open("rb").read())
    
    def release(self):
        pass