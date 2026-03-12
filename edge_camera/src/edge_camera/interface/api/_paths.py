import os
from pathlib import Path


def output_dir(camera_id: str) -> Path:
    """Resolve the output directory for a given camera.

    Priority: CAMERA_OUTPUT_DIR env var → /dev/shm/vio (Linux) → /tmp/vio (macOS/other).
    """
    shm = Path("/dev/shm")
    default = shm / "vio" if shm.is_dir() else Path("/tmp/vio")
    base = Path(os.getenv("CAMERA_OUTPUT_DIR", "")) or default
    return base / camera_id
