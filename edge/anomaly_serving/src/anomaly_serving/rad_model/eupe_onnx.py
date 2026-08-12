"""Shared EUPE ONNX encoder: catalogue, weight resolution and inference session.

Vendored from the 2026-anomaly-detection research repository at commit bea4d0b
(``lib/models/eupe_onnx.py``).  The only local modification is the docstring
below: upstream's AnomalyEUPE detector is not vendored here, so RAD's backbone
adapter is this module's sole consumer in the service.

This module is the single low-level entry point to the EUPE ViT encoders.  It
owns the ONNX catalogue, the local-override resolution, the OpenVINO / ONNX
Runtime session and the fixed 224x224 preprocessing — and it deliberately knows
nothing about anomaly detection.

Upstream has two independent consumers — the AnomalyEUPE *method* (dual
global/local scoring) and the :class:`FeatureBackbone` adapter that lets RAD tap
the same encoder.  Only the second is vendored here, as
:mod:`anomaly_serving.rad_model.backbones.eupe`; this service serves RAD and never
reaches the AnomalyEUPE code paths (which would drag in cv2, scipy and sklearn).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image

EUPE_ONNX_CATALOGUE: dict[str, tuple[str, int]] = {
    "eupe_vitt16": ("eupe_vitt16.onnx", 192),
    "eupe_vitt16_int8": ("eupe_vitt16_int8.onnx", 192),
    "eupe_vits16": ("eupe_vits16.onnx", 384),
    "eupe_vits16_int8": ("eupe_vits16_int8.onnx", 384),
    "eupe_vitb16": ("eupe_vitb16.onnx", 768),
    "eupe_vitb16_int8": ("eupe_vitb16_int8.onnx", 768),
}

EUPE_MODEL_CHOICES: tuple[str, ...] = tuple(EUPE_ONNX_CATALOGUE)

EUPE_HF_REPO = "rockerritesh/EUPE-ONNX"
EUPE_FIXED_ONNX_DIR = Path("weights/eupe-onnx-fixed")
EUPE_FIXED_INT8_FILES = {
    "eupe_vits16_int8": "eupe_vits16_int8.onnx",
    "eupe_vitb16_int8": "eupe_vitb16_int8.onnx",
}

# Fixed spatial layout for all ViT-*/16 ONNX models at 224x224.
EUPE_INPUT_SIZE = 224
EUPE_GRID_H = 14
EUPE_GRID_W = 14
EUPE_NUM_PATCHES = EUPE_GRID_H * EUPE_GRID_W  # 196

# ImageNet normalisation constants, laid out for HWC numpy arrays.
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def resolve_eupe_onnx_path(model_name: str) -> str:
    """Return a local repaired ONNX path when present, otherwise HF cache."""
    fixed_filename = EUPE_FIXED_INT8_FILES.get(model_name)
    if fixed_filename is not None:
        fixed_path = EUPE_FIXED_ONNX_DIR / fixed_filename
        if fixed_path.exists():
            return str(fixed_path)

    filename, _ = EUPE_ONNX_CATALOGUE[model_name]
    return hf_hub_download(repo_id=EUPE_HF_REPO, filename=filename)


def eupe_embed_dim(model_name: str) -> int:
    """Token dimensionality of an EUPE catalogue entry."""
    _, embed_dim = EUPE_ONNX_CATALOGUE[model_name]
    return embed_dim


def preprocess_eupe_image(img: np.ndarray) -> np.ndarray:
    """Convert HWC-RGB uint8 -> (1, 3, 224, 224) float32 ImageNet-normalised."""
    pil = Image.fromarray(img).resize(
        (EUPE_INPUT_SIZE, EUPE_INPUT_SIZE), Image.BICUBIC
    )
    x = np.array(pil, dtype=np.float32) / 255.0
    x = (x - _MEAN) / _STD
    return x.transpose(2, 0, 1)[None].astype(np.float32)


class _Runner:
    """Minimal interface: ``run(input_array) -> (cls_token, patch_tokens)``."""

    backend: str
    device: str

    def run(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError


class _OpenVINORunner(_Runner):
    backend = "openvino"

    def __init__(self, model_path: str, device: str) -> None:
        import openvino as ov

        core = ov.Core()
        available = set(core.available_devices) | {"AUTO"}
        chosen = device.upper()
        if chosen not in available:
            chosen = "CPU"
        model = core.read_model(model_path)
        # Force f32 inference precision: the EUPE ViT overflows to NaN under
        # the GPU's default fp16 hint (every real image produces NaN tokens).
        config = {"INFERENCE_PRECISION_HINT": "f32"}
        self._compiled = core.compile_model(model, chosen, config)
        self.device = chosen

    def run(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        result = self._compiled(x)
        cls_token = result[0]
        patch_tokens = result[1]
        return cls_token, patch_tokens


class _OrtRunner(_Runner):
    backend = "onnxruntime"

    def __init__(self, model_path: str, device: str) -> None:
        import onnxruntime as ort

        providers = ort.get_available_providers()
        self._session = ort.InferenceSession(model_path, providers=providers)
        self.device = "CPU"

    def run(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        cls_token, patch_tokens = self._session.run(None, {"input": x})
        return cls_token, patch_tokens


def _build_runner(model_path: str, device: str) -> _Runner:
    """Pick the best inference backend for the requested device."""
    try:
        return _OpenVINORunner(model_path, device)
    except Exception:
        return _OrtRunner(model_path, device)


class EUPESession:
    """Frozen EUPE ViT encoder behind an OpenVINO / ONNX Runtime session.

    Parameters
    ----------
    model_name : str
        One of :data:`EUPE_ONNX_CATALOGUE`.  Append ``_int8`` for the quantised
        variant.
    device : str
        ``"GPU"`` (Intel/AMD/NVIDIA via OpenVINO), ``"CPU"``, or ``"AUTO"``.
        Falls back to ONNX Runtime CPU when OpenVINO is unavailable.
    """

    def __init__(self, model_name: str = "eupe_vitb16", device: str = "GPU") -> None:
        if model_name not in EUPE_ONNX_CATALOGUE:
            raise ValueError(
                f"Unknown EUPE model_name={model_name!r}. "
                f"Choose from: {sorted(EUPE_ONNX_CATALOGUE)}"
            )
        self.model_name = model_name
        self.embed_dim = eupe_embed_dim(model_name)
        self._runner = _build_runner(resolve_eupe_onnx_path(model_name), device)

    @property
    def backend(self) -> str:
        return self._runner.backend

    @property
    def device(self) -> str:
        return self._runner.device

    def extract(self, img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Encode a single HWC-RGB uint8 image.

        Returns
        -------
        cls_token : (D,) float32
        patch_tokens : (196, D) float32
        """
        cls_token, patch_tokens = self._runner.run(preprocess_eupe_image(img))
        return cls_token[0], patch_tokens[0]

    def extract_many(self, images: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        """Encode a list of HWC-RGB uint8 images.

        The ONNX graphs are exported with a static batch of 1, so this loops;
        it exists to give callers a single batched-looking entry point.

        Returns
        -------
        cls_tokens : (N, D) float32
        patch_tokens : (N, 196, D) float32
        """
        cls_list: list[np.ndarray] = []
        patch_list: list[np.ndarray] = []
        for img in images:
            cls_token, patch_tokens = self.extract(img)
            cls_list.append(np.asarray(cls_token, dtype=np.float32))
            patch_list.append(np.asarray(patch_tokens, dtype=np.float32))
        return np.stack(cls_list, axis=0), np.stack(patch_list, axis=0)
