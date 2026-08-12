"""Shared constants used across the vendored RAD model code.

Vendored verbatim from the 2026-anomaly-detection research repository at commit
bea4d0b (``lib/utils/constants.py``).
"""

from __future__ import annotations

# ImageNet channel statistics used by every backbone that expects images
# normalised the torchvision way.  Kept here as the single source of truth so
# transforms, inference de-normalisation and the demo agree exactly.
IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)
