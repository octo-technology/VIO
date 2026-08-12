"""The backbone contract shared by retrieval-based detectors.

Vendored verbatim from the 2026-anomaly-detection research repository at commit
bea4d0b (``lib/models/backbones/base.py``).

A backbone is a *frozen feature extractor* and nothing else: it turns a batch of
ImageNet-normalised images into per-layer CLS and patch tokens.  It owns no
memory bank, no scoring rule and no anomaly map — those belong to the detector
(RAD, ...) that consumes it.  Detectors therefore never import each other to
borrow an encoder; they ask for one through this API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

import torch
import torch.nn as nn


class FeatureBackbone(nn.Module, ABC):
    """Frozen multi-layer CLS/patch token extractor.

    Subclasses load their weights lazily, on the first :meth:`extract` call, so
    that constructing a detector never triggers a download or a session build.
    """

    #: Registry key, e.g. ``"dinov3"``.  Set by each subclass.
    name: str = ""

    def __init__(self, layer_indices: Iterable[int]) -> None:
        super().__init__()
        self._layer_indices = self.resolve_layer_indices(layer_indices)

    @classmethod
    def resolve_layer_indices(cls, layer_indices: Iterable[int]) -> tuple[int, ...]:
        """Normalise requested taps to the ones this backbone can actually serve.

        Classmethod on purpose: callers need the resolved taps *before* any
        weights are loaded (to size their memory banks), and some backbones
        expose a single fused layer whatever was asked for.
        """
        indices = tuple(sorted(int(index) for index in layer_indices))
        if not indices:
            raise ValueError(f"{cls.__name__} requires at least one layer index.")
        return indices

    @property
    def layer_indices(self) -> tuple[int, ...]:
        """Layers tapped by :meth:`extract`, in the order it returns them."""
        return self._layer_indices

    @property
    def num_layers(self) -> int:
        return len(self._layer_indices)

    @property
    def config(self) -> dict[str, Any]:
        """Backbone identity, for logging and checkpoint metadata."""
        return {"backbone": self.name, "layer_indices": list(self._layer_indices)}

    @abstractmethod
    def extract(
        self, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        """Encode an ImageNet-normalised ``(B, 3, H, W)`` batch.

        Returns
        -------
        patch_tokens : list of ``(B, P, C)`` fp32 tensors, one per entry of
            :attr:`layer_indices`, on ``images.device``.
        cls_tokens : list of ``(B, C)`` fp32 tensors, same ordering.
        """

    def forward(
        self, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        return self.extract(images)
