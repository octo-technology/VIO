from abc import abstractmethod
from typing import Dict, Type, Union

from edge_orchestrator.domain.models.business_rules.camera_business_rules.expected_label_rule import (
    ExpectedLabelRule,
)
from edge_orchestrator.domain.models.business_rules.camera_business_rules.max_nb_objects_rule import (
    MaxNbObjectsRule,
)
from edge_orchestrator.domain.models.business_rules.camera_business_rules.min_nb_objects_rule import (
    MinNbObjectsRule,
)
from edge_orchestrator.domain.models.business_rules.camera_rule import CameraRule


def get_camera_rule(rule_name) -> Type[CameraRule]:
    if rule_name == "expected_label_rule":
        return ExpectedLabelRule
    elif rule_name == "min_nb_objects_rule":
        return MinNbObjectsRule
    elif rule_name == "max_nb_objects_rule":
        return MaxNbObjectsRule
    else:
        raise NotImplementedError


def get_last_inference_by_camera(inference: Dict) -> Dict:
    last_model = list(inference.keys())[len(inference) - 1]
    last_model_inference = inference[last_model]
    return last_model_inference


class Camera:
    @abstractmethod
    def __init__(self, id: str, settings: Dict[str, Union[str, Dict]]):
        self.id = id
        self.settings = settings

    @abstractmethod
    def capture(self) -> bytes:
        pass

    @abstractmethod
    def apply_settings(self, settings: Dict):
        pass
