import io

import aiohttp
import numpy as np
from PIL import Image, ImageOps

from edge_orchestrator import logger
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.ports.model_forward import ModelForward


class TFServingClassificationWrapper(ModelForward):
    def __init__(self, base_url):
        self.base_url = base_url
        self.class_names = None

    async def perform_inference(
        self, model: ModelInfos, binary_data: bytes, binary_name: str
    ) -> dict:
        self.class_names = model.class_names
        processed_img = self.perform_pre_processing(model, binary_data)
        payload = {"inputs": processed_img.tolist()}
        model_url = (
            f"{self.base_url}/v1/models/{model.name}/versions/{model.version}:predict"
        )
        logger.info(f"Getting prediction using: {model_url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(model_url, json=payload) as response:
                    json_data = await response.json()
            inference_output = self.perform_post_processing(
                model, json_data["outputs"], binary_name
            )
            return inference_output
        except Exception as e:
            logger.exception(e)
            inference_output = "NO_DECISION"
            return inference_output

    def perform_pre_processing(self, model: ModelInfos, binary: bytes):
        data = np.ndarray(
            shape=(1, model.image_resolution[0], model.image_resolution[1], 3),
            dtype=np.float32,
        )
        img = Image.open(io.BytesIO(binary))
        img = ImageOps.fit(
            img, (model.image_resolution[0], model.image_resolution[1]), Image.ANTIALIAS
        )
        img_array = np.asarray(img)
        normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array
        return data

    def perform_post_processing(
        self, model: ModelInfos, json_outputs: list, binary_name: str
    ) -> dict:
        return {
            binary_name: {
                "label": model.class_names[np.argmax(json_outputs[0])],
                "probability": float(np.max(json_outputs[0])),
            }
        }
