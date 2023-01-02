from abc import abstractmethod
from enum import Enum
from typing import Dict

from edge_orchestrator.domain.models.model_infos import ModelInfos


class Labels(Enum):
    KO = 'KO'
    OK = 'OK'
    NO_DECISION = 'NO_DECISION'


class ModelForward:

    @abstractmethod
    async def perform_inference(self, model: ModelInfos, binary_data: bytes, binary_name: str) -> Dict[str, Dict]:
        pass
