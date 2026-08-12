"""Discovery and loading of fitted RAD models from disk.

A RAD model is a directory under ``MODELS_PATH`` holding two files:

``model.ckpt``
    A ``torch.save`` blob written by the research repo's export script (or by
    ``RADModule.save_checkpoint``): ``{"hparams", "layers", "cls_banks",
    "patch_banks", "fitted"}``.  It carries the fitted memory bank, so no
    reference images are needed at serving time.  Encoder weights are *not* in
    the blob — they are pulled from HuggingFace / torch.hub on first use.
``metadata.json``
    Serving configuration: resize, decision method/param, threshold, and the
    backbone selection.  Values here override the checkpoint's own hparams, so a
    threshold can be retuned without refitting.
"""

from __future__ import annotations

import json
import logging
import os
from inspect import signature
from pathlib import Path
from typing import Any, Dict

import torch

from anomaly_serving.rad_model.decision import (
    DEFAULT_DECISION_METHOD,
    resolve_decision_param,
)
from anomaly_serving.rad_model.rad import RAD

DEFAULT_RESIZE = 224
DEFAULT_THRESHOLD = 0.5

# Constructor keyword names accepted by RAD, used to filter checkpoint hparams
# (which also carry Lightning-only keys such as ``max_ratio``).
_RAD_INIT_FIELDS = frozenset(signature(RAD.__init__).parameters) - {"self"}


def _get_models_path() -> Path:
    return Path(os.getenv("MODELS_PATH")) if os.getenv("MODELS_PATH") else Path.cwd() / "models"


def get_models_path() -> Path:
    """Public accessor for the models root (``MODELS_PATH`` or ``./models``)."""
    return _get_models_path()


def load_model_metadata(model_dir: Path) -> dict:
    metadata_path = model_dir / "metadata.json"
    if not metadata_path.exists():
        logging.warning(f"No metadata.json found for model at {model_dir}. Serving defaults will be used.")
        return {}
    with metadata_path.open() as f:
        return json.load(f)


def load_rad_model(ckpt_path: Path, metadata: dict) -> RAD:
    """Rebuild a fitted :class:`RAD` from a checkpoint plus serving metadata."""
    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)

    # metadata.json wins over the checkpoint's fit-time hparams so that backbone
    # and retrieval settings can be corrected without a refit.
    kwargs: Dict[str, Any] = {k: v for k, v in dict(state.get("hparams", {})).items() if k in _RAD_INIT_FIELDS}
    kwargs.update({k: v for k, v in metadata.items() if k in _RAD_INIT_FIELDS})

    if "layer_indices" not in kwargs and state.get("layers"):
        kwargs["layer_indices"] = tuple(state["layers"])
    if "layer_indices" in kwargs:
        kwargs["layer_indices"] = tuple(kwargs["layer_indices"])

    model = RAD(**kwargs)
    if not state.get("fitted", False):
        raise ValueError(f"Checkpoint at {ckpt_path} holds no fitted memory bank")
    model.set_memory(state["cls_banks"], state["patch_banks"])
    model.eval()
    logging.info(
        f"Loaded RAD model {ckpt_path.parent.name} from {ckpt_path.resolve()} "
        f"(backbone={model.backbone}, layers={model.layer_indices}, "
        f"bank={model.cls_banks[-1].shape[0]} images)"
    )
    return model


def warm_up(model: RAD, resize: int) -> None:
    """Run one throwaway prediction so the first real request is not the slow one.

    RAD builds its backbone lazily on the first ``predict`` — for the EUPE path
    that means downloading the ONNX file and compiling it under OpenVINO, tens of
    seconds of work.  It also normalises the memory banks onto the compute device
    and caches the patch-window geometry.  Paying all of that at startup keeps the
    first inspection as fast as every later one.
    """
    model.predict(torch.zeros(1, 3, resize, resize))


def resolve_serving_config(metadata: dict) -> Dict[str, Any]:
    """Extract the serving-side knobs (resize / decision / threshold)."""
    method = metadata.get("decision_method", DEFAULT_DECISION_METHOD)
    return {
        "resize": int(metadata.get("resize", DEFAULT_RESIZE)),
        "decision_method": method,
        "decision_param": resolve_decision_param(method, metadata.get("decision_param")),
        "threshold": float(metadata.get("threshold", DEFAULT_THRESHOLD)),
    }


def create_model_registry() -> Dict[str, RAD]:
    """Load every fitted RAD model found under ``MODELS_PATH``.

    A model that fails to load is logged and skipped rather than aborting
    startup — torch/HuggingFace loads can fail on a missing download or a
    corrupt checkpoint, and one bad model should not take the service down.
    """
    registry: Dict[str, RAD] = {}
    models_path = _get_models_path()
    logging.info(f"rad_models_path: {models_path.resolve()}")
    if not models_path.exists():
        return registry
    for ckpt_path in sorted(models_path.glob("**/model.ckpt")):
        model_name = ckpt_path.parent.name
        try:
            metadata = load_model_metadata(ckpt_path.parent)
            model = load_rad_model(ckpt_path, metadata)
            warm_up(model, resolve_serving_config(metadata)["resize"])
            registry[model_name] = model
            logging.info(f"Model '{model_name}' warmed up and ready")
        except Exception:
            logging.exception(f"Failed to load RAD model '{model_name}' from {ckpt_path} — skipping")
    return registry


def create_model_metadata_registry() -> Dict[str, dict]:
    registry: Dict[str, dict] = {}
    models_path = _get_models_path()
    if not models_path.exists():
        return registry
    for model_dir in models_path.iterdir():
        if model_dir.is_dir():
            registry[model_dir.name] = load_model_metadata(model_dir)
    return registry
