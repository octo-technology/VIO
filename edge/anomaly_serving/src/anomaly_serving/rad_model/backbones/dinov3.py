"""DINOv3 ViT backbone (Hugging Face ``transformers`` or ``torch.hub``).

Vendored from the 2026-anomaly-detection research repository at commit bea4d0b
(``lib/models/backbones/dinov3.py``), import path only.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any, Iterable

import torch
import torch.nn as nn

from anomaly_serving.rad_model.backbones.base import FeatureBackbone

DINOV3_HF_MODEL_ID = "facebook/dinov3-vitb16-pretrain-lvd1689m"
DINOV3_LOCAL_HF_DIR = Path("weights/dinov3-vitb16-pretrain-lvd1689m")
DINOV3_TORCH_HUB_NAME = "dinov3_vitb16"
DINOV3_ENCODER_CHOICES = (
    "facebook/dinov3-vits16-pretrain-lvd1689m",
    "facebook/dinov3-vits16plus-pretrain-lvd1689m",
    DINOV3_HF_MODEL_ID,
    "facebook/dinov3-vitl16-pretrain-lvd1689m",
    "facebook/dinov3-vith16plus-pretrain-lvd1689m",
    "facebook/dinov3-vit7b16-pretrain-lvd1689m",
)
DINOV3_WEIGHT_CHOICES = (
    ("Auto (local cache or Hugging Face)", ""),
    ("Local ViT-B/16 download", str(DINOV3_LOCAL_HF_DIR)),
)


class DinoV3Backbone(FeatureBackbone):
    """Frozen DINOv3 ViT exposing intermediate-block CLS/patch tokens.

    Parameters
    ----------
    layer_indices :
        Zero-based transformer block indices to tap.
    encoder_name :
        Hugging Face model id, a local directory, or a ``torch.hub`` entry name.
    encoder_weights :
        Optional local weights directory (``transformers`` layout) or ``.pth``
        state dict for the ``torch.hub`` entry.
    use_amp :
        Run the frozen forward under autocast (fp16) on CUDA / XPU.  Tokens are
        always cast back to fp32 before being returned, so consumers stay
        dtype-stable.
    """

    name = "dinov3"

    def __init__(
        self,
        layer_indices: Iterable[int] = (3, 6, 9, 11),
        encoder_name: str = DINOV3_HF_MODEL_ID,
        encoder_weights: str | None = None,
        use_amp: bool = False,
    ) -> None:
        super().__init__(layer_indices)
        self.encoder_name = encoder_name
        self.encoder_weights = encoder_weights
        self.use_amp = bool(use_amp)

        self.encoder: nn.Module | None = None
        self._backend: str | None = None

    @property
    def config(self) -> dict[str, Any]:
        return {
            **super().config,
            "encoder_name": self.encoder_name,
            "encoder_weights": self.encoder_weights,
        }

    # ------------------------------------------------------------------
    # Weight resolution / lazy loading
    # ------------------------------------------------------------------

    def _hf_encoder_source(self) -> str | Path | None:
        if self.encoder_weights:
            weights_path = Path(self.encoder_weights).expanduser()
            if weights_path.is_dir():
                return weights_path

        encoder_path = Path(self.encoder_name).expanduser()
        if encoder_path.is_dir():
            return encoder_path

        if DINOV3_LOCAL_HF_DIR.is_dir() and self.encoder_name in {
            DINOV3_HF_MODEL_ID,
            DINOV3_TORCH_HUB_NAME,
        }:
            return DINOV3_LOCAL_HF_DIR

        if self.encoder_name.startswith("facebook/dinov3-"):
            return self.encoder_name

        return None

    def _ensure_encoder(self, device: torch.device) -> nn.Module:
        if self.encoder is None:
            hf_source = self._hf_encoder_source()
            if hf_source is not None:
                from transformers import AutoModel

                local_files_only = isinstance(hf_source, Path)
                encoder = AutoModel.from_pretrained(
                    hf_source,
                    local_files_only=local_files_only,
                )
                self._backend = "transformers"
            elif self.encoder_weights:
                encoder = torch.hub.load(
                    "facebookresearch/dinov3",
                    self.encoder_name,
                    pretrained=False,
                    trust_repo=True,
                )
                state = torch.load(
                    Path(self.encoder_weights).expanduser(), map_location="cpu"
                )
                encoder.load_state_dict(state, strict=True)
                self._backend = "torchhub"
            else:
                encoder = torch.hub.load(
                    "facebookresearch/dinov3",
                    self.encoder_name,
                    pretrained=True,
                    trust_repo=True,
                )
                self._backend = "torchhub"
            encoder.eval()
            for param in encoder.parameters():
                param.requires_grad = False
            self.encoder = encoder
        self.encoder.to(device)
        self.encoder.eval()
        return self.encoder

    def _autocast(self, device: torch.device):
        """Autocast context for the frozen forward (no-op unless AMP).

        Half precision is only enabled on accelerators that support it (CUDA /
        XPU); CPU falls back to a null context so the encoder still runs in
        fp32 there.
        """
        if not self.use_amp or device.type not in ("cuda", "xpu"):
            return contextlib.nullcontext()
        return torch.autocast(device_type=device.type, dtype=torch.float16)

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    @torch.no_grad()
    def extract(
        self, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        encoder: Any = self._ensure_encoder(images.device)
        # Run the frozen encoder forward under autocast when AMP is enabled,
        # then cast the extracted tokens back to fp32 so downstream memory
        # banks and cosine similarities stay dtype-stable regardless of the
        # autocast dtype.
        with self._autocast(images.device):
            if self._backend == "transformers":
                return self._extract_transformers(encoder, images)

            outputs = encoder.get_intermediate_layers(  # pyright: ignore[reportCallIssue]
                images,
                n=list(self.layer_indices),
                return_class_token=True,
                reshape=False,
                norm=True,
            )
        hub_patch_tokens = []
        hub_cls_tokens = []
        for patch_tok, cls_tok in outputs:
            hub_patch_tokens.append(patch_tok.float())
            hub_cls_tokens.append(cls_tok.float())
        return hub_patch_tokens, hub_cls_tokens

    def _extract_transformers(
        self, encoder: Any, images: torch.Tensor
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        outputs = encoder(
            pixel_values=images,
            output_hidden_states=True,
            return_dict=True,
        )
        hidden_states = outputs.hidden_states
        if hidden_states is None:
            raise RuntimeError("Transformers DINOv3 did not return hidden states.")
        num_register_tokens = int(
            getattr(getattr(encoder, "config", None), "num_register_tokens", 0)
        )
        num_prefix_tokens = 1 + num_register_tokens
        norm = getattr(encoder, "norm", None)

        patch_tokens: list[torch.Tensor] = []
        cls_tokens: list[torch.Tensor] = []
        for layer_index in self.layer_indices:
            hidden_index = layer_index + 1
            if hidden_index >= len(hidden_states):
                raise ValueError(
                    f"DINOv3 layer index {layer_index} is out of range for "
                    f"{self.encoder_name}; got {len(hidden_states) - 1} blocks."
                )
            hidden = hidden_states[hidden_index]
            if norm is not None:
                hidden = norm(hidden)
            cls_tokens.append(hidden[:, 0, :].float())
            patch_tokens.append(hidden[:, num_prefix_tokens:, :].float())
        return patch_tokens, cls_tokens
