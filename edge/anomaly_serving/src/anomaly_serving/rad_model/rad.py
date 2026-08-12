"""RAD: Retrieval-based Anomaly Detection.

Vendored from the 2026-anomaly-detection research repository at commit bea4d0b
(``lib/models/rad.py``).  Do not hand-edit the algorithm here — re-vendor the
file when upstream changes.  The only local modification is the import path of
the backbone package (``lib.models`` -> ``anomaly_serving.rad_model``).

The image-level score returned by :meth:`RAD.predict` is ignored by this
service: ``anomaly_serving`` recomputes it from the returned anomaly map so that the
decision method (raw score / mean of top fraction / percentile) is a serving
concern rather than a fit-time constant.  See ``anomaly_serving.rad_model.decision``.

Reference
---------
Zhang, X., Li, G., Henderson, P., Aragon-Camarasa, G., & Long, Z. (2026).
"Is Training Necessary for Anomaly Detection?" arXiv:2601.22763.

This implementation follows the paper and official code:
- Frozen DINOv3 ViT-B/16 encoder.
- Multi-layer memory from transformer blocks 4, 7, 10, and 12
  (zero-based indices 3, 6, 9, 11 in the official implementation).
- Last-layer CLS token global retrieval over anomaly-free images.
- Patch-level 1-NN cosine dissimilarity inside the retrieved image set.
- Optional spatial conditioning with an L-infinity patch-grid radius.
- Uniform multi-layer score fusion by default.
- Image score from the mean of the top 1% pixels after Gaussian smoothing.

The encoder is reached through :mod:`lib.models.backbones`, so swapping DINOv3
for another frozen extractor (EUPE, ...) never drags another detector's scoring
logic in with it.
"""

from __future__ import annotations

from typing import Iterable

import torch
import torch.nn as nn
import torch.nn.functional as F

from anomaly_serving.rad_model.backbones import FeatureBackbone, build_backbone, resolve_layer_indices
from anomaly_serving.rad_model.backbones.dinov3 import (
    DINOV3_ENCODER_CHOICES,
    DINOV3_HF_MODEL_ID,
    DINOV3_LOCAL_HF_DIR,
    DINOV3_TORCH_HUB_NAME,
    DINOV3_WEIGHT_CHOICES,
)

# Backwards-compatible aliases: the DINOv3 catalogue now lives with the
# backbone, but the CLI / demo surfaces still import it from here.
RAD_HF_MODEL_ID = DINOV3_HF_MODEL_ID
RAD_LOCAL_HF_DIR = DINOV3_LOCAL_HF_DIR
RAD_TORCH_HUB_NAME = DINOV3_TORCH_HUB_NAME
RAD_ENCODER_CHOICES = DINOV3_ENCODER_CHOICES
RAD_WEIGHT_CHOICES = DINOV3_WEIGHT_CHOICES


def _gaussian_filter(kernel_size: int = 5, sigma: float = 1.0) -> nn.Conv2d:
    coords = torch.arange(kernel_size)
    x_grid = coords.repeat(kernel_size).view(kernel_size, kernel_size)
    y_grid = x_grid.t()
    xy_grid = torch.stack([x_grid, y_grid], dim=-1).float()
    mean = (kernel_size - 1) / 2.0
    variance = sigma**2
    kernel = (1.0 / (2.0 * torch.pi * variance)) * torch.exp(
        -torch.sum((xy_grid - mean) ** 2.0, dim=-1) / (2.0 * variance)
    )
    kernel = kernel / kernel.sum()
    kernel = kernel.view(1, 1, kernel_size, kernel_size)
    conv = nn.Conv2d(
        1,
        1,
        kernel_size=kernel_size,
        groups=1,
        bias=False,
        padding=kernel_size // 2,
    )
    conv.weight.data = kernel
    conv.weight.requires_grad = False
    return conv


class RAD(nn.Module):
    """Training-free RAD model with a multi-layer anomaly-free memory bank.

    ``backbone`` selects the frozen encoder by registry key (``"dinov3"``,
    ``"eupe"``); everything else here — retrieval, patch scoring, fusion, the
    anomaly map — is RAD's own and identical across backbones.
    """

    def __init__(
        self,
        encoder_name: str = RAD_HF_MODEL_ID,
        encoder_weights: str | None = None,
        layer_indices: tuple[int, ...] = (3, 6, 9, 11),
        k_image: int = 150,
        pos_radius: int = 1,
        use_positional_bank: bool = True,
        resize_mask: int = 256,
        max_ratio: float = 0.01,
        layer_weights: tuple[float, ...] | None = None,
        use_amp: bool = False,
        backbone: str = "dinov3",
        eupe_model_name: str = "eupe_vitb16",
        eupe_device: str = "GPU",
    ) -> None:
        super().__init__()
        # ``backbone`` is the registry *key*; the extractor itself is built
        # below as ``self.feature_backbone``.
        self.backbone = str(backbone)
        self.eupe_model_name = eupe_model_name
        self.eupe_device = eupe_device
        self.encoder_name = encoder_name
        self.encoder_weights = encoder_weights
        # Each backbone decides which taps it can serve (the EUPE ONNX export
        # exposes a single fused CLS/patch token layer, so RAD's multi-layer
        # memory collapses to one layer there).
        self.layer_indices = resolve_layer_indices(self.backbone, layer_indices)
        self.k_image = int(k_image)
        self.pos_radius = int(pos_radius)
        self.use_positional_bank = bool(use_positional_bank)
        self.resize_mask = int(resize_mask)
        self.max_ratio = float(max_ratio)
        self.layer_weights = self._normalise_layer_weights(layer_weights)
        # Mixed-precision inference: hold the L2-normalised memory banks in
        # half precision here, and (for torch backbones) run the frozen forward
        # under autocast.  Off by default so training / benchmark runs stay
        # bit-reproducible in fp32; the live/demo builder opts in for lower
        # per-frame latency and roughly half the patch-bank bandwidth cost.
        self.use_amp = bool(use_amp)

        # Frozen feature extractor behind the shared backbone API.  Built here
        # but loaded lazily, so constructing a RAD never triggers a download.
        self.feature_backbone: FeatureBackbone = build_backbone(
            self.backbone,
            self.layer_indices,
            **self._backbone_options(),
        )

        self.cls_banks: list[torch.Tensor] = []
        self.patch_banks: list[torch.Tensor] = []
        self._fitted = False
        # Cache of (window_idx, window_valid) tensors for the positional bank,
        # keyed by (grid_side, pos_radius, device); depends only on the patch
        # grid geometry, so it is built once and reused across frames.
        self._pos_window_cache: dict[
            tuple[int, int, str], tuple[torch.Tensor, torch.Tensor]
        ] = {}
        # Pre-normalised memory banks materialised on the compute device once
        # per (fit, device) and reused across frames.
        self._bank_device: str | None = None
        self._cls_bank_global_norm: torch.Tensor | None = None
        self._patch_banks_norm: list[torch.Tensor] = []

        self.register_buffer("_device_ref", torch.empty(0), persistent=False)
        self.gaussian = _gaussian_filter(kernel_size=5, sigma=1.0)

    def _backbone_options(self) -> dict[str, object]:
        """Constructor options for the selected backbone."""
        if self.backbone == "eupe":
            return {
                "model_name": self.eupe_model_name,
                "device": self.eupe_device,
            }
        return {
            "encoder_name": self.encoder_name,
            "encoder_weights": self.encoder_weights,
            "use_amp": self.use_amp,
        }

    def _bank_dtype(self) -> torch.dtype:
        return torch.float16 if self.use_amp else torch.float32

    @staticmethod
    def _normalise_layer_weights(
        layer_weights: Iterable[float] | None,
    ) -> tuple[float, ...] | None:
        if layer_weights is None:
            return None
        weights = tuple(float(w) for w in layer_weights)
        total = sum(weights)
        if total <= 0:
            return None
        return tuple(w / total for w in weights)

    def _weights_for_layers(self) -> tuple[float, ...]:
        num_layers = len(self.layer_indices)
        if self.layer_weights is None or len(self.layer_weights) != num_layers:
            return tuple(1.0 / num_layers for _ in range(num_layers))
        return self.layer_weights

    def _ensure_device_banks(self, device: torch.device) -> None:
        """Materialise L2-normalised memory banks on *device* once and cache them.

        The banks are stored on CPU by :meth:`set_memory`; the first prediction
        on a given device uploads and normalises them a single time, and every
        subsequent frame reuses the cached device tensors directly.
        """
        if not self._fitted:
            return
        dev_key = str(device)
        if self._bank_device == dev_key and self._cls_bank_global_norm is not None:
            return
        bank_dtype = self._bank_dtype()
        # Normalise in fp32 for numerical stability, then store in the bank
        # dtype (fp16 under AMP) to halve the memory-bandwidth cost of the
        # per-frame ``index_select`` + similarity einsum over the patch banks.
        self._cls_bank_global_norm = F.normalize(
            self.cls_banks[-1].to(device, dtype=torch.float32), dim=-1
        ).to(bank_dtype)
        self._patch_banks_norm = [
            F.normalize(bank.to(device, dtype=torch.float32), dim=-1).to(bank_dtype)
            for bank in self.patch_banks
        ]
        self._bank_device = dev_key

    @torch.no_grad()
    def extract_multilayer(
        self, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        """Per-layer ``(patch_tokens, cls_tokens)`` from the frozen backbone."""
        return self.feature_backbone.extract(images)

    def set_memory(
        self,
        cls_banks: list[torch.Tensor],
        patch_banks: list[torch.Tensor],
    ) -> None:
        if len(cls_banks) != len(self.layer_indices):
            raise ValueError("cls_banks length must match layer_indices length.")
        if len(patch_banks) != len(self.layer_indices):
            raise ValueError("patch_banks length must match layer_indices length.")
        self.cls_banks = [bank.detach().cpu() for bank in cls_banks]
        self.patch_banks = [bank.detach().cpu() for bank in patch_banks]
        self._fitted = True
        # Invalidate any previously cached on-device banks.
        self._bank_device = None
        self._cls_bank_global_norm = None
        self._patch_banks_norm = []

    @torch.no_grad()
    def fit(self, images: torch.Tensor, batch_size: int = 8) -> None:
        """Build RAD memory from a tensor of normal images."""
        cls_chunks: list[list[torch.Tensor]] = [
            [] for _ in range(len(self.layer_indices))
        ]
        patch_chunks: list[list[torch.Tensor]] = [
            [] for _ in range(len(self.layer_indices))
        ]
        for batch in images.split(batch_size):
            patch_tokens, cls_tokens = self.extract_multilayer(batch)
            for layer_idx in range(len(self.layer_indices)):
                cls_chunks[layer_idx].append(cls_tokens[layer_idx].cpu())
                patch_chunks[layer_idx].append(patch_tokens[layer_idx].cpu())
        self.set_memory(
            [torch.cat(chunks, dim=0) for chunks in cls_chunks],
            [torch.cat(chunks, dim=0) for chunks in patch_chunks],
        )

    def _positional_window(
        self, grid_side: int, device: torch.device
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Precompute the L-infinity patch-window neighbour indices and mask.

        Returns ``(window_idx, window_valid)`` of shape ``(num_patches, W)``
        with ``W = (2 * pos_radius + 1) ** 2``.  ``window_idx`` holds the flat
        patch index of each in-window neighbour (out-of-grid positions clamped
        to a valid index) and ``window_valid`` masks the positions that fall
        outside the grid.  The result depends only on the grid geometry, so it
        is cached and reused across frames.
        """
        key = (grid_side, self.pos_radius, str(device))
        cached = self._pos_window_cache.get(key)
        if cached is not None:
            return cached

        radius = self.pos_radius
        rows = torch.arange(grid_side, device=device)
        cols = torch.arange(grid_side, device=device)
        patch_row = rows.view(-1, 1).expand(grid_side, grid_side).reshape(-1)
        patch_col = cols.view(1, -1).expand(grid_side, grid_side).reshape(-1)

        idx_cols: list[torch.Tensor] = []
        valid_cols: list[torch.Tensor] = []
        for d_row in range(-radius, radius + 1):
            for d_col in range(-radius, radius + 1):
                nbr_row = patch_row + d_row
                nbr_col = patch_col + d_col
                valid = (
                    (nbr_row >= 0)
                    & (nbr_row < grid_side)
                    & (nbr_col >= 0)
                    & (nbr_col < grid_side)
                )
                nbr_row_c = nbr_row.clamp(0, grid_side - 1)
                nbr_col_c = nbr_col.clamp(0, grid_side - 1)
                idx_cols.append(nbr_row_c * grid_side + nbr_col_c)
                valid_cols.append(valid)

        window_idx = torch.stack(idx_cols, dim=1).long()
        window_valid = torch.stack(valid_cols, dim=1)
        self._pos_window_cache[key] = (window_idx, window_valid)
        return window_idx, window_valid

    @staticmethod
    def _positional_patch_score(
        query: torch.Tensor,
        neighbor_features: torch.Tensor,
        window_idx: torch.Tensor,
        window_valid: torch.Tensor,
    ) -> torch.Tensor:
        """Vectorised spatially-conditioned patch score.

        Computes ``1 - max cosine similarity`` between each query patch and the
        retrieved neighbour patches within its L-infinity window, matching the
        per-patch loop but without any Python iteration over patches.

        Parameters
        ----------
        query : (num_patches, C) — L2-normalised query patch features.
        neighbor_features : (k_image, num_patches, C) — L2-normalised retrieved
            reference patches.
        window_idx / window_valid : (num_patches, W) — window neighbour indices
            and their in-grid validity mask.
        """
        num_patches, window_size = window_idx.shape
        running_max = query.new_full((num_patches,), -float("inf"))
        neg_inf = query.new_tensor(-float("inf"))
        for offset in range(window_size):
            gathered = neighbor_features.index_select(1, window_idx[:, offset])
            # (k_image, num_patches) similarity of each patch to its neighbour
            # at this window offset across all retrieved reference images.
            sim = torch.einsum("kpc,pc->kp", gathered, query).amax(dim=0)
            sim = torch.where(window_valid[:, offset], sim, neg_inf)
            running_max = torch.maximum(running_max, sim)
        return 1.0 - running_max

    @torch.no_grad()
    def predict(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if not self._fitted:
            raise RuntimeError("RAD memory bank is empty; fit/build it first.")

        device = images.device
        self._ensure_device_banks(device)
        self.gaussian.to(device)

        patch_list, cls_list = self.extract_multilayer(images)
        num_layers = len(self.layer_indices)
        num_bank_images = self.cls_banks[-1].shape[0]
        k_image = min(max(1, self.k_image), num_bank_images)

        cls_bank_global = self._cls_bank_global_norm
        assert cls_bank_global is not None  # guaranteed by _ensure_device_banks
        # Match the (possibly fp16) bank dtype so the retrieval matmul / einsum
        # don't hit a dtype mismatch; normalisation itself stays in fp32.
        bank_dtype = cls_bank_global.dtype
        cls_x_global = F.normalize(cls_list[-1], dim=-1).to(bank_dtype)
        sim_img = torch.matmul(cls_x_global, cls_bank_global.t())
        _, topk_idx = torch.topk(sim_img, k_image, dim=-1)

        batch_size, num_patches, channels = patch_list[0].shape
        grid_side = int(num_patches**0.5)
        if grid_side * grid_side != num_patches:
            raise ValueError("RAD expects a square ViT patch grid.")

        layer_weights = self._weights_for_layers()
        if self.use_positional_bank:
            window_idx, window_valid = self._positional_window(grid_side, device)
        batch_patch_scores: list[torch.Tensor] = []
        for batch_idx in range(batch_size):
            neighbor_indices = topk_idx[batch_idx]
            scores_per_layer: list[torch.Tensor] = []

            for layer_idx in range(num_layers):
                query = F.normalize(patch_list[layer_idx][batch_idx], dim=-1).to(
                    bank_dtype
                )
                # Banks are already L2-normalised on-device (see
                # ``_ensure_device_banks``), so slicing the neighbours is enough.
                neighbor_features = self._patch_banks_norm[layer_idx][neighbor_indices]

                if self.use_positional_bank:
                    patch_score = self._positional_patch_score(
                        query, neighbor_features, window_idx, window_valid
                    )
                else:
                    local_bank = neighbor_features.reshape(-1, channels)
                    sim = torch.matmul(query, local_bank.t())
                    nn_sim = sim.max(dim=-1).values
                    patch_score = 1.0 - nn_sim

                scores_per_layer.append(patch_score)

            fused = torch.zeros_like(scores_per_layer[0])
            for layer_idx in range(num_layers):
                fused = fused + layer_weights[layer_idx] * scores_per_layer[layer_idx]
            batch_patch_scores.append(fused)

        # Back to fp32 for the map upsample + fp32 Gaussian conv and scoring.
        patch_scores = torch.stack(batch_patch_scores, dim=0).float()
        patch_maps = patch_scores.view(batch_size, 1, grid_side, grid_side)
        anomaly_maps_4d = F.interpolate(
            patch_maps,
            size=(self.resize_mask, self.resize_mask),
            mode="bilinear",
            align_corners=False,
        )
        anomaly_maps_4d = self.gaussian(anomaly_maps_4d)

        if self.max_ratio <= 0:
            image_scores = anomaly_maps_4d.flatten(1).max(dim=1).values
        else:
            flat = anomaly_maps_4d.flatten(1)
            top_k = max(1, int(flat.shape[1] * self.max_ratio))
            image_scores = torch.sort(flat, dim=1, descending=True).values[
                :, :top_k
            ].mean(dim=1)

        return image_scores, anomaly_maps_4d[:, 0]

    def forward(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        return self.predict(images)
