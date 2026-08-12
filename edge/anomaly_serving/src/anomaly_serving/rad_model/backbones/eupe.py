"""EUPE ONNX backbone adapter.

Vendored from the 2026-anomaly-detection research repository at commit bea4d0b
(``lib/models/backbones/eupe.py``), import path only.

Wraps the shared :class:`anomaly_serving.rad_model.eupe_onnx.EUPESession` in the
:class:`FeatureBackbone` contract so torch-side detectors can tap the EUPE
encoder.  This is the *only* bridge between EUPE and RAD — the AnomalyEUPE
method is a separate detector that happens to use the same encoder (and is not
vendored into this service), and neither imports the other.
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import torch

from anomaly_serving.rad_model.backbones.base import FeatureBackbone
from anomaly_serving.rad_model.eupe_onnx import (
    EUPE_MODEL_CHOICES,
    EUPE_ONNX_CATALOGUE,
    EUPESession,
    eupe_embed_dim,
)
from anomaly_serving.rad_model.constants import IMAGENET_MEAN, IMAGENET_STD

__all__ = ["EUPEBackbone", "EUPE_MODEL_CHOICES"]


class EUPEBackbone(FeatureBackbone):
    """Frozen EUPE ViT (ONNX) exposing a single fused CLS/patch token layer.

    The exported graphs emit one CLS token and one 14x14 patch-token grid — no
    intermediate blocks — so this backbone always resolves to a single layer,
    whatever taps the caller asks for.

    Parameters
    ----------
    layer_indices :
        Accepted and ignored beyond arity; see :meth:`resolve_layer_indices`.
    model_name :
        One of :data:`EUPE_MODEL_CHOICES`.
    device :
        Inference device hint passed to the ONNX session (``"GPU"``, ``"CPU"``
        or ``"AUTO"``).  Independent of the torch device the tokens land on.
    """

    name = "eupe"

    def __init__(
        self,
        layer_indices: Iterable[int] = (0,),
        model_name: str = "eupe_vitb16",
        device: str = "GPU",
    ) -> None:
        super().__init__(layer_indices)
        if model_name not in EUPE_ONNX_CATALOGUE:
            raise ValueError(
                f"Unknown EUPE model_name={model_name!r}. "
                f"Choose from: {sorted(EUPE_ONNX_CATALOGUE)}"
            )
        self.model_name = model_name
        self.device_hint = device
        self.embed_dim = eupe_embed_dim(model_name)
        self._session: EUPESession | None = None

    @classmethod
    def resolve_layer_indices(cls, layer_indices: Iterable[int]) -> tuple[int, ...]:
        """Always ``(0,)``: the ONNX export exposes one fused token layer."""
        return (0,)

    @property
    def config(self) -> dict[str, Any]:
        return {
            **super().config,
            "eupe_model_name": self.model_name,
            "embed_dim": self.embed_dim,
        }

    def _ensure_session(self) -> EUPESession:
        if self._session is None:
            self._session = EUPESession(self.model_name, device=self.device_hint)
        return self._session

    @staticmethod
    def _to_rgb_uint8(images: torch.Tensor) -> list[np.ndarray]:
        """De-normalise an ImageNet batch to a list of HWC uint8 RGB arrays.

        The ONNX graph owns its own preprocessing (bicubic resize to 224 then
        ImageNet normalisation), so the torch-side normalisation has to be
        undone first.
        """
        mean = torch.tensor(IMAGENET_MEAN, device=images.device).view(1, 3, 1, 1)
        std = torch.tensor(IMAGENET_STD, device=images.device).view(1, 3, 1, 1)
        rgb = ((images * std + mean) * 255.0).clamp(0, 255).byte()
        return [rgb[i].permute(1, 2, 0).cpu().numpy() for i in range(rgb.shape[0])]

    @torch.no_grad()
    def extract(
        self, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        session = self._ensure_session()
        cls_np, patch_np = session.extract_many(self._to_rgb_uint8(images))
        cls_tokens = torch.from_numpy(cls_np).to(images.device)
        patch_tokens = torch.from_numpy(patch_np).to(images.device)
        return [patch_tokens], [cls_tokens]
