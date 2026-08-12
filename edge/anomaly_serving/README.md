# Edge RAD serving

Serves **RAD** (Retrieval-based Anomaly Detection) models for VIO inspection
pipelines. RAD is training-free: instead of learning a classifier, it stores
frozen-backbone features of anomaly-free reference images in a memory bank, then
scores a test image by how far its patches sit from their nearest neighbours in
that bank.

This is a sibling of `edge/tflite_serving` and exposes the **same HTTP contract**,
so the orchestrator needs no changes — a pipeline step simply points its
`model_serving_url` here instead.

## Why a separate service

`edge/tflite_serving` is deliberately lightweight (TFLite interpreter, numpy,
pillow). RAD needs PyTorch plus an ONNX runtime, which would roughly quadruple
that image for deployments that never use anomaly detection. Keeping RAD separate
means only sites that want it pay for it.

## Running

```shell
make install     # create .venv and install dependencies
make serve       # run on port 8502 with reload
make unit_tests  # run the test suite
make check       # lint and format check
```

Or via Docker from the repository root:

```shell
make edge_anomaly_serving      # this service only
make vio-edge-up           # the whole edge stack, including this service
```

## API

| Route | Purpose |
|---|---|
| `GET /v1/models` | Names of loaded models |
| `GET /v1/capabilities` | Per-model version, `output_type`, `class_names` |
| `GET /v1/models/{name}/metadata` | Input shape plus RAD config (backbone, resize, decision method, threshold) |
| `POST /v1/models/{name}/versions/{version}:predict` | Raw image bytes in (`application/octet-stream`), prediction out |

```shell
curl -X POST --data-binary @part.jpg \
  -H "Content-Type: application/octet-stream" \
  http://localhost:8502/v1/models/my_part/versions/1:predict
```

```json
{
  "prediction_type": "class",
  "label": "KO",
  "probability": 0.61,
  "raw_score": 0.4881,
  "decision_method": "mean_top_fraction",
  "decision_param": 0.01,
  "threshold": 0.4
}
```

`prediction_type`, `label`, and `probability` are exactly what
`tflite_serving`'s classification models return, which is what lets the
orchestrator and its `expected_label_rule` camera rule consume RAD predictions
unchanged. `probability` is a *display* confidence, normalised so that the
threshold sits at 0.5 — the real anomaly score is `raw_score`, which has no fixed
upper bound.

## Decision methods

RAD produces a per-pixel anomaly map. Turning that into one score is configured
per model in `metadata.json`:

| `decision_method` | `decision_param` | Behaviour |
|---|---|---|
| `raw_score` | unused | The single most anomalous pixel. Most sensitive, most noise-prone |
| `mean_top_fraction` | fraction, default `0.01` | Mean of the top 1% of pixels. The paper's default and a good starting point |
| `percentile` | quantile, default `0.99` | True P99 of the pixel distribution. Ignores how extreme the very worst pixels are, so it is steadier than `mean_top_fraction` on images with a few hot pixels |

An item is `KO` when its score is at or above `threshold`.

## Backbones

| `backbone` | Runtime | Latency/image | Notes |
|---|---|---|---|
| `eupe` | ONNX via OpenVINO, ONNX Runtime fallback | ~37–190 ms | The only edge-viable option. `eupe_vitt16` is fastest, `eupe_vitb16` the most accurate of the three |
| `dinov3` | PyTorch + transformers | ~500 ms–2.2 s | Higher accuracy, but too slow for Raspberry-Pi-class hardware. Use on a mini-PC or GPU host |

Latency figures come from the research repo's KSDD benchmark; re-run
`benchmark.py` on your target hardware before committing to a variant.

Backbone weights are **not** baked into the image — they download on first use
into `HF_HOME`, which the compose file backs with a named volume so restarts
don't re-download. First startup therefore needs network access.

Every model runs one throwaway prediction during startup, which forces the
backbone download and the OpenVINO compile to happen before the service accepts
traffic. Without that warmup the first real inspection paid the whole cost — ~29 s
against ~0.3 s once warm — so startup is slower by design and inference is not.

## Adding a model

See [models/README.md](models/README.md). In short: fit a memory bank on
anomaly-free images with `scripts/export_rad_bank.py` in the
2026-anomaly-detection repo, then drop the resulting `model.ckpt` and
`metadata.json` into `models/<model_name>/` and restart.

Models and their `metadata.json` are read once at startup, so editing a
threshold takes effect on the next restart.

## Using it in a pipeline

Add a pipeline step to a station config pointing at this service:

```json
{
  "camera_id": "camera_1",
  "model_forwarder_config": {
    "model_name": "my_part",
    "model_version": "1",
    "model_serving_url": "http://edge_anomaly_serving:8502/"
  },
  "camera_rule_config": {
    "camera_rule_type": "expected_label_rule",
    "expected_class": "OK"
  }
}
```

## Vendored code

Copied from the 2026-anomaly-detection research repo (commit `bea4d0b`):

| Here | Upstream |
|---|---|
| `rad_model/rad.py` | `lib/models/rad.py` |
| `rad_model/eupe_onnx.py` | `lib/models/eupe_onnx.py` |
| `rad_model/constants.py` | `lib/utils/constants.py` |
| `rad_model/backbones/` | `lib/models/backbones/` |

The only local change is the import path (`lib.models` / `lib.utils` →
`anomaly_serving.rad_model`); each file's docstring records it. Re-vendor rather
than hand-editing when upstream changes. `rad_model/decision.py` is *not*
vendored — image-level scoring is this service's own concern.

Upstream reaches its encoders through a `FeatureBackbone` registry, so RAD no
longer contains any DINOv3 or EUPE loading code of its own — swapping backbones
is a registry lookup. That is why `lib/models/anomalyeupe.py` is no longer
vendored: the EUPE ONNX session moved into `eupe_onnx.py`, and RAD reaches it
through `backbones/eupe.py` instead of borrowing the AnomalyEUPE detector. This
service serves RAD only, so it never needs AnomalyEUPE's dual-scoring path — and
with it goes that file's `cv2` / `scipy` / `sklearn` weight.
