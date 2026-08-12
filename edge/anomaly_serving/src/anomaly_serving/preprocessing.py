"""Image preprocessing shared by the predict and fit paths.

Both a prediction and a memory-bank fit must feed the backbone identically —
same resize, same ImageNet normalisation — or the fitted references and the
test image would live in different feature spaces. Keeping the single transform
here guarantees they cannot drift apart.
"""

import io

import numpy as np
import torch
from PIL import Image

# RAD's backbones are trained on ImageNet-normalised inputs.
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def preprocess_image(image: Image.Image, resize: int) -> torch.Tensor:
    """Resize an image to the model's input square and ImageNet-normalise it.

    Returns a ``(1, 3, resize, resize)`` float tensor.
    """
    image = image.convert("RGB").resize((resize, resize), Image.Resampling.BILINEAR)
    arr = np.array(image, dtype=np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
    return torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)


def preprocess_bytes(data: bytes, resize: int) -> torch.Tensor:
    """Decode raw image bytes and preprocess them (see :func:`preprocess_image`)."""
    return preprocess_image(Image.open(io.BytesIO(data)), resize)
