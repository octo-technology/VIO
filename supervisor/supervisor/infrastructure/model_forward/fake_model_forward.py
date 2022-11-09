import random
from typing import Dict
import numpy as np

from supervisor.domain.models.model_infos import ModelInfos, ModelTypes
from supervisor.domain.ports.model_forward import ModelForward, Labels


class FakeModelForward(ModelForward):
    async def perform_inference(self, model: ModelInfos, binary_data: bytes, binary_name: str) -> Dict:
        inference_output = {}
        if model.category == ModelTypes.CLASSIFICATION.value:
            inference_output = {
                binary_name:
                    {
                        'label': random.choice([Labels.OK.value, Labels.KO.value]),
                        'probability': np.random.uniform(0, 1)
                    }
            }

        elif model.category == ModelTypes.OBJECT_DETECTION.value:
            inference_output = {
                f'{binary_name}_object_1': {
                    'location': [4, 112, 244, 156],
                    'objectness': np.random.uniform(0, 1),
                },
                f'{binary_name}_object_2': {
                    'location': [4, 112, 244, 156],
                    'objectness': np.random.uniform(0, 1)
                }
            }

        elif model.category == ModelTypes.OBJECT_DETECTION_WITH_CLASSIFICATION.value:
            inference_output = {
                f'{binary_name}_object_1': {
                    'location': [4, 112, 244, 156],
                    'objectness': np.random.uniform(0, 1),
                    'label': random.choice([Labels.OK.value, Labels.KO.value]),
                    'probability': np.random.uniform(0, 1)
                },
                f'{binary_name}_object_2': {
                    'location': [4, 112, 244, 156],
                    'objectness': np.random.uniform(0, 1),
                    'label': random.choice([Labels.OK.value, Labels.KO.value]),
                    'probability': np.random.uniform(0, 1)
                }
            }
        return inference_output
