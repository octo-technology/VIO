import asyncio
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Awaitable, Callable, Dict, Optional

from PIL import Image as PilImage

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend

_FAKE_WIDTH = 640
_FAKE_HEIGHT = 480
_FAKE_COLOR = (100, 149, 237)  # cornflower blue


class FakeCameraBackend(ICameraBackend):
    """In-memory fake camera for testing. Generates solid-colour JPEG frames."""

    def __init__(self, width: int = _FAKE_WIDTH, height: int = _FAKE_HEIGHT, color: tuple = _FAKE_COLOR):
        self._width = width
        self._height = height
        self._color = color
        self._frame_interval: float = 0.1  # seconds between push-mode frames

    def _generate_frame_bytes(self) -> bytes:
        img = PilImage.new("RGB", (self._width, self._height), self._color)
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        path = output_dir / filename
        frame_bytes = self._generate_frame_bytes()
        path.write_bytes(frame_bytes)
        return ImageRef.from_path(path, camera_id)

    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        while True:
            image_ref = await self.capture(output_dir, camera_id)
            await on_frame(image_ref)
            await asyncio.sleep(self._frame_interval)

    def health(self) -> Dict:
        return {"status": "ok", "type": "fake"}

    def metadata(self) -> Dict:
        return {
            "type": "fake",
            "resolution": [self._width, self._height],
            "fps": int(1 / self._frame_interval),
        }
