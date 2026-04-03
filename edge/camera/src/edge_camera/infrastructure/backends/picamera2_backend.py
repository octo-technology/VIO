import asyncio
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable, Dict

try:
    from picamera2 import Picamera2

    _PICAMERA2_AVAILABLE = True
except ImportError:
    _PICAMERA2_AVAILABLE = False
    Picamera2 = None  # type: ignore[assignment,misc]

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend


class Picamera2Backend(ICameraBackend):
    """Camera backend using picamera2 (Raspberry Pi CSI cameras)."""

    def __init__(self, camera_num: int = 0) -> None:
        if not _PICAMERA2_AVAILABLE:
            raise RuntimeError("picamera2 is required: pip install 'edge_camera[raspberry]'")
        self._camera_num = camera_num
        self._frame_interval: float = 1 / 30  # ~30 fps in push mode

    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture_sync, output_dir, camera_id)

    def _capture_sync(self, output_dir: Path, camera_id: str) -> ImageRef:
        cam = Picamera2(self._camera_num)
        try:
            cam.start()
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            cam.capture_file(str(filename))
            return ImageRef.from_path(filename, camera_id)
        finally:
            cam.stop()
            cam.close()

    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        loop = asyncio.get_event_loop()
        cam = Picamera2(self._camera_num)
        try:
            cam.start()
            while True:
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                await loop.run_in_executor(None, cam.capture_file, str(filename))
                ref = ImageRef.from_path(filename, camera_id)
                await on_frame(ref)
                await asyncio.sleep(self._frame_interval)
        finally:
            cam.stop()
            cam.close()

    def health(self) -> Dict:
        try:
            cam = Picamera2(self._camera_num)
            cam.close()
            return {"status": "ok", "type": "picamera2", "camera_num": self._camera_num}
        except Exception as exc:
            return {"status": "error", "type": "picamera2", "camera_num": self._camera_num, "error": str(exc)}

    def metadata(self) -> Dict:
        cam = Picamera2(self._camera_num)
        try:
            props = cam.camera_properties
            size = props.get("PixelArraySize", [0, 0])
            return {
                "type": "picamera2",
                "camera_num": self._camera_num,
                "model": props.get("Model", "unknown"),
                "resolution": f"{size[0]}x{size[1]}",
            }
        finally:
            cam.close()
