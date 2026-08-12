"""Building and persisting a RAD memory bank from anomaly-free images.

This is the serving layer's own concern, not part of the vendored ``rad_model``
package: RAD knows how to *fit* a bank from a batch of images, but it has no
notion of growing one incrementally or of writing it to the on-disk checkpoint
format the registry reads back. Both live here.

Incremental append is what lets the dashboard "teach the good part" a few images
at a time — each call extracts the new images' features and concatenates them
onto the existing bank rather than refitting from scratch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import torch

from anomaly_serving.rad_model.rad import RAD
from anomaly_serving.rad_registry import _RAD_INIT_FIELDS

ProgressCallback = Callable[[int], None]


@torch.no_grad()
def append_reference_images(
    model: RAD,
    images: torch.Tensor,
    batch_size: int = 8,
    progress_cb: ProgressCallback | None = None,
) -> int:
    """Extend ``model``'s memory bank with more anomaly-free images.

    Extracts backbone features for ``images`` and concatenates them onto the
    model's existing per-layer banks (or seeds the banks if the model has none
    yet), then commits the result with :meth:`RAD.set_memory`. ``progress_cb``,
    if given, is called with the running count of processed images after each
    batch. Returns the total number of images in the bank afterwards.
    """
    num_layers = len(model.layer_indices)
    new_cls: list[list[torch.Tensor]] = [[] for _ in range(num_layers)]
    new_patch: list[list[torch.Tensor]] = [[] for _ in range(num_layers)]

    processed = 0
    for batch in images.split(batch_size):
        patch_tokens, cls_tokens = model.extract_multilayer(batch)
        for layer_idx in range(num_layers):
            new_cls[layer_idx].append(cls_tokens[layer_idx].detach().cpu())
            new_patch[layer_idx].append(patch_tokens[layer_idx].detach().cpu())
        processed += int(batch.shape[0])
        if progress_cb is not None:
            progress_cb(processed)

    # A non-empty ``cls_banks`` is the public signal that the model is already
    # fitted; seed from scratch otherwise.
    has_existing_bank = bool(model.cls_banks)
    cls_banks = [
        torch.cat(([model.cls_banks[i]] if has_existing_bank else []) + new_cls[i], dim=0) for i in range(num_layers)
    ]
    patch_banks = [
        torch.cat(([model.patch_banks[i]] if has_existing_bank else []) + new_patch[i], dim=0)
        for i in range(num_layers)
    ]
    model.set_memory(cls_banks, patch_banks)
    return int(model.cls_banks[-1].shape[0])


def save_checkpoint(model: RAD, ckpt_path: Path) -> None:
    """Persist a fitted model to the checkpoint format the registry loads.

    Written to a sibling temp file and atomically renamed so a crash mid-write
    can never leave a half-serialised ``model.ckpt`` that would fail to load on
    the next boot.
    """
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "hparams": {field: getattr(model, field) for field in _RAD_INIT_FIELDS if hasattr(model, field)},
        "layers": list(model.layer_indices),
        "cls_banks": model.cls_banks,
        "patch_banks": model.patch_banks,
        "fitted": bool(model.cls_banks),
    }
    tmp_path = ckpt_path.with_name(ckpt_path.name + ".tmp")
    torch.save(state, tmp_path)
    tmp_path.replace(ckpt_path)
