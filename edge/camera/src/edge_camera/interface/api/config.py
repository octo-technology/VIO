"""Pydantic-backed configuration for the edge_camera service.

Load order (last wins):
  1. Defaults defined here
  2. YAML file at CAMERA_CONFIG_FILE env var (default: ./camera_config.yml) if it exists
  3. CAMERA_OUTPUT_DIR and CAMERA_PUSH_URL env vars for simple overrides

YAML format example::

    output_dir: /dev/shm/vio
    push_url: http://edge-orchestrator:8000/api/v1/push
    cameras:
      cam_1:
        backend: opencv
        device_index: 0
      cam_2:
        backend: basler
        serial_number: "12345678"
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CameraBackendConfig(BaseModel):
    backend: str = "fake"
    device_index: int = 0
    camera_num: int = 0
    serial_number: Optional[str] = None


class CameraServiceConfig(BaseModel):
    output_dir: Optional[str] = None
    push_url: str = ""
    cameras: Dict[str, CameraBackendConfig] = Field(default_factory=lambda: {"cam_1": CameraBackendConfig()})

    @classmethod
    def load(cls) -> "CameraServiceConfig":
        config_file = Path(os.getenv("CAMERA_CONFIG_FILE", "camera_config.yml"))
        data: dict = {}
        if config_file.exists():
            with config_file.open() as f:
                data = yaml.safe_load(f) or {}
            logger.info("Loaded camera config from %s", config_file)
        else:
            logger.debug("No config file found at %s, using defaults / env vars", config_file)

        # Parse cameras sub-section if present
        raw_cameras = data.pop("cameras", None)
        config = cls(**data)

        if raw_cameras:
            config = config.model_copy(
                update={"cameras": {k: CameraBackendConfig(**v) for k, v in raw_cameras.items()}}
            )

        # Env var overrides for simple scalars
        if output_dir := os.getenv("CAMERA_OUTPUT_DIR"):
            config = config.model_copy(update={"output_dir": output_dir})
        if push_url := os.getenv("CAMERA_PUSH_URL"):
            config = config.model_copy(update={"push_url": push_url})

        return config
