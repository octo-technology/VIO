# RAD models

One directory per model, named after the `model_name` a pipeline step refers to.
Each holds two files:

```
models/
  my_part/
    model.ckpt        # fitted memory bank (torch.save blob)
    metadata.json     # serving configuration
```

Both are produced by `scripts/export_rad_bank.py` in the
[2026-anomaly-detection](https://github.com/josselinonduty/2026-anomaly-detection)
repository, which fits RAD on a directory of anomaly-free reference images:

```shell
python scripts/export_rad_bank.py \
    --images_dir data/my_part/train/good \
    --score_images_dir data/my_part/heldout \
    --backbone eupe --eupe_model_name eupe_vitb16 \
    --resize 224 \
    --decision_method mean_top_fraction --decision_param 0.01 \
    --output_dir /tmp/rad_my_part
```

`--score_images_dir` should hold images kept *out* of the fit — a mix of normal
and defective ones is ideal. The script prints their score distribution so you
can place `--threshold` between the two clusters, then copy both output files
here. Scoring the fitted images instead tells you nothing: each one is its own
nearest neighbour in the memory bank, so it always scores ~0.

`model.ckpt` files are large (the memory bank grows with the number of reference
images) and are deliberately not committed — see `.gitignore`.

## metadata.json

```json
{
  "version": "1",
  "output_type": "anomaly",
  "class_names": ["OK", "KO"],
  "normalization": "imagenet",

  "backbone": "eupe",
  "eupe_model_name": "eupe_vitb16",
  "eupe_device": "AUTO",
  "encoder_name": "facebook/dinov3-vitb16-pretrain-lvd1689m",
  "encoder_weights": null,
  "layer_indices": [0],

  "resize": 224,
  "k_image": 150,
  "pos_radius": 1,
  "use_positional_bank": true,
  "resize_mask": 256,

  "decision_method": "mean_top_fraction",
  "decision_param": 0.01,
  "threshold": 0.35
}
```

Values here override the checkpoint's own fit-time hyperparameters, so a
threshold can be retuned by editing this file and restarting the service — no
refit needed.

| Field | Meaning |
|---|---|
| `backbone` | `eupe` (ONNX/OpenVINO, edge-viable) or `dinov3` (torch/transformers, higher accuracy, much slower) |
| `eupe_model_name` | EUPE variant when `backbone: eupe` — `eupe_vitt16`/`eupe_vits16`/`eupe_vitb16`, optionally `_int8` |
| `eupe_device` | OpenVINO device for the EUPE session — `GPU` (default), `CPU`, or `AUTO`. Unavailable devices fall back to `CPU`, so `AUTO` is the safe choice on heterogeneous fleets |
| `encoder_name` | DINOv3 model id when `backbone: dinov3` |
| `layer_indices` | Backbone blocks feeding the memory bank. Forced to `[0]` for `eupe` |
| `resize` | Input square size. Must match the `--resize` used at fit time |
| `k_image` | Number of reference images retrieved per query |
| `pos_radius` | Spatial patch-window radius for neighbour-constrained retrieval |
| `decision_method` | `raw_score`, `mean_top_fraction`, or `percentile` |
| `decision_param` | Top fraction for `mean_top_fraction` (0.01 = top 1%), quantile for `percentile` (0.99 = P99), unused for `raw_score` |
| `threshold` | Score at or above which the item is `KO` |
