"""Image-level scoring and OK/KO decision for RAD anomaly maps.

RAD returns a per-pixel anomaly map; turning that map into a single score and a
pass/fail verdict is a serving concern, so it lives here rather than inside the
vendored model.  Three aggregation methods are supported:

``raw_score``
    The single most anomalous pixel.  Most sensitive, most noise-prone.
``mean_top_fraction``
    Mean of the top ``decision_param`` fraction of pixels (the paper's default,
    with ``decision_param=0.01`` giving the mean of the top 1%).
``percentile``
    The ``decision_param`` quantile of the pixel distribution — ``0.99`` gives a
    true P99.  Unlike ``mean_top_fraction`` this is a single order statistic, so
    it ignores how extreme the very worst pixels are.
"""

from __future__ import annotations

import torch

RAW_SCORE = "raw_score"
MEAN_TOP_FRACTION = "mean_top_fraction"
PERCENTILE = "percentile"

DECISION_METHODS = (RAW_SCORE, MEAN_TOP_FRACTION, PERCENTILE)

DEFAULT_DECISION_METHOD = MEAN_TOP_FRACTION
DEFAULT_DECISION_PARAMS = {
    RAW_SCORE: 0.0,
    MEAN_TOP_FRACTION: 0.01,
    PERCENTILE: 0.99,
}

LABEL_OK = "OK"
LABEL_KO = "KO"


def compute_score(anomaly_map: torch.Tensor, method: str, param: float) -> float:
    """Aggregate a single image's anomaly map into one image-level score.

    Parameters
    ----------
    anomaly_map : torch.Tensor
        Per-pixel anomaly scores for one image, any shape (flattened here).
    method : str
        One of :data:`DECISION_METHODS`.
    param : float
        Top fraction in ``(0, 1]`` for ``mean_top_fraction``, quantile in
        ``[0, 1]`` for ``percentile``, ignored for ``raw_score``.
    """
    flat = anomaly_map.detach().flatten().float()
    if flat.numel() == 0:
        raise ValueError("Cannot score an empty anomaly map")

    if method == RAW_SCORE:
        return float(flat.max())

    if method == MEAN_TOP_FRACTION:
        if not 0.0 < param <= 1.0:
            raise ValueError(f"{MEAN_TOP_FRACTION} expects a fraction in (0, 1], got {param}")
        top_k = max(1, int(flat.numel() * param))
        return float(torch.topk(flat, top_k).values.mean())

    if method == PERCENTILE:
        if not 0.0 <= param <= 1.0:
            raise ValueError(f"{PERCENTILE} expects a quantile in [0, 1], got {param}")
        return float(torch.quantile(flat, param))

    raise ValueError(f"Unknown decision_method '{method}'; expected one of {DECISION_METHODS}")


def decide(score: float, threshold: float) -> str:
    """Classify a score as OK or KO. At exactly the threshold the item is KO."""
    return LABEL_KO if score >= threshold else LABEL_OK


def normalize_confidence(score: float, threshold: float) -> float:
    """Map an unbounded anomaly score onto ``[0, 1]`` for display purposes.

    The cockpit renders a prediction's ``probability`` as a percentage, so the
    raw anomaly score (which has no fixed upper bound) cannot go in that field.
    This maps the threshold to the midpoint — 0 stays 0, ``threshold`` becomes
    0.5, and anything at or above twice the threshold saturates at 1.0 — so the
    displayed percentage crossing 50% lines up with the OK/KO flip.  The true
    score is reported separately as ``raw_score``.
    """
    if threshold <= 0:
        return 1.0 if score > 0 else 0.0
    return min(1.0, max(0.0, score / (2.0 * threshold)))


def resolve_decision_param(method: str, param: float | None) -> float:
    """Fall back to the method's conventional default when unset."""
    if param is not None:
        return float(param)
    if method not in DEFAULT_DECISION_PARAMS:
        raise ValueError(f"Unknown decision_method '{method}'; expected one of {DECISION_METHODS}")
    return DEFAULT_DECISION_PARAMS[method]
