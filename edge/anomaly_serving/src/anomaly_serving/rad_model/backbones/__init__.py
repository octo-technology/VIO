"""Frozen feature backbones behind one API.

Vendored from the 2026-anomaly-detection research repository at commit bea4d0b
(``lib/models/backbones/``).  The only local modification across this package is
the import path (``lib.models`` / ``lib.utils`` -> ``anomaly_serving.rad_model``).

Detectors declare *which* encoder they want by name and receive a
:class:`FeatureBackbone`; they never import another detector to reach an
encoder.  Adding a backbone means adding a subclass here and one registry
entry — no detector changes.

    backbone = build_backbone("eupe", layer_indices=(0,), model_name="eupe_vitb16")
    patch_tokens, cls_tokens = backbone.extract(images)
"""

from __future__ import annotations

from typing import Any, Iterable

from anomaly_serving.rad_model.backbones.base import FeatureBackbone
from anomaly_serving.rad_model.backbones.dinov3 import (
    DINOV3_ENCODER_CHOICES,
    DINOV3_HF_MODEL_ID,
    DINOV3_LOCAL_HF_DIR,
    DINOV3_TORCH_HUB_NAME,
    DINOV3_WEIGHT_CHOICES,
    DinoV3Backbone,
)
from anomaly_serving.rad_model.backbones.eupe import EUPE_MODEL_CHOICES, EUPEBackbone

BACKBONE_REGISTRY: dict[str, type[FeatureBackbone]] = {
    DinoV3Backbone.name: DinoV3Backbone,
    EUPEBackbone.name: EUPEBackbone,
}

BACKBONE_CHOICES: tuple[str, ...] = tuple(BACKBONE_REGISTRY)


def get_backbone_class(name: str) -> type[FeatureBackbone]:
    """Look up a backbone class by registry key."""
    try:
        return BACKBONE_REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"Unknown backbone {name!r}. Choose from: {sorted(BACKBONE_REGISTRY)}"
        ) from None


def build_backbone(
    name: str,
    layer_indices: Iterable[int],
    **options: Any,
) -> FeatureBackbone:
    """Instantiate a backbone by name.

    ``options`` are backbone-specific keyword arguments (see each subclass):
    ``encoder_name`` / ``encoder_weights`` / ``use_amp`` for ``dinov3``,
    ``model_name`` / ``device`` for ``eupe``.  Weights are loaded lazily, so
    this call is cheap.
    """
    return get_backbone_class(name)(layer_indices=layer_indices, **options)


def resolve_layer_indices(name: str, layer_indices: Iterable[int]) -> tuple[int, ...]:
    """Resolve requested taps for a backbone without instantiating it."""
    return get_backbone_class(name).resolve_layer_indices(layer_indices)


__all__ = [
    "BACKBONE_CHOICES",
    "BACKBONE_REGISTRY",
    "DINOV3_ENCODER_CHOICES",
    "DINOV3_HF_MODEL_ID",
    "DINOV3_LOCAL_HF_DIR",
    "DINOV3_TORCH_HUB_NAME",
    "DINOV3_WEIGHT_CHOICES",
    "EUPE_MODEL_CHOICES",
    "DinoV3Backbone",
    "EUPEBackbone",
    "FeatureBackbone",
    "build_backbone",
    "get_backbone_class",
    "resolve_layer_indices",
]
