import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict

try:
    import cv2

    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    cv2 = None  # type: ignore[assignment]

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend


class OpenCvCameraBackend(ICameraBackend):
    """Camera backend using OpenCV VideoCapture (USB/CSI/V4L2 devices)."""

    def __init__(self, device_index: int = 0) -> None:
        if not _CV2_AVAILABLE:
            raise RuntimeError("opencv-python-headless is required: pip install 'edge_camera[usb]'")
        self._frame_interval: float = 1 / 30  # ~30 fps in push mode
        self._cap: Any = cv2.VideoCapture(device_index)  # type: ignore[union-attr]
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera device {device_index}")

    def __del__(self) -> None:
        if hasattr(self, "_cap") and self._cap.isOpened():
            self._cap.release()

    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture_sync, output_dir, camera_id)

    def _capture_sync(self, output_dir: Path, camera_id: str) -> ImageRef:
        ret, frame = self._cap.read()
        if not ret:
            raise RuntimeError(f"Failed to read frame from camera {camera_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        cv2.imwrite(str(filename), frame)
        return ImageRef.from_path(filename, camera_id)

    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        while True:
            ret, frame = self._cap.read()
            if ret:
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                cv2.imwrite(str(filename), frame)
                ref = ImageRef.from_path(filename, camera_id)
                await on_frame(ref)
            await asyncio.sleep(self._frame_interval)

    def health(self) -> Dict:
        return {"status": "ok" if self._cap.isOpened() else "error", "type": "opencv"}

    def metadata(self) -> Dict:
        return {
            "type": "opencv",
            "resolution": f"{int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
            "fps": self._cap.get(cv2.CAP_PROP_FPS),
        }
