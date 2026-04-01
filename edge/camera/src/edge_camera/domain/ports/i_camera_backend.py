from abc import ABC, abstractmethod
from pathlib import Path
from typing import Awaitable, Callable, Dict

from edge_camera.domain.models.image_ref import ImageRef


class ICameraBackend(ABC):
    @abstractmethod
    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        """Capture a single frame, write it to output_dir, and return an ImageRef."""

    @abstractmethod
    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        """Push mode: block until cancelled, calling on_frame for each triggered frame."""

    @abstractmethod
    def health(self) -> Dict:
        """Return health status for this backend."""

    @abstractmethod
    def metadata(self) -> Dict:
        """Return static metadata (type, resolution, fps, etc.)."""
