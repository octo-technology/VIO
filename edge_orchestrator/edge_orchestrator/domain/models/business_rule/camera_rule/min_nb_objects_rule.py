from typing import Dict, Union

from edge_orchestrator.domain.models.business_rule.camera_rule.camera_rule import (
    CameraRule,
)
from edge_orchestrator.domain.models.decision import Decision


class MinNbObjectsRule(CameraRule):
    def __init__(self, class_to_detect: str, min_threshold: int):
        self.class_to_detect = class_to_detect
        self.min_threshold = min_threshold

    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        objects_of_interest = [obj for obj in inference if obj in self.class_to_detect]

        if len(inference) == 0:
            camera_decision = Decision.NO_DECISION
        elif len(objects_of_interest) < self.min_threshold:
            camera_decision = Decision.KO
        else:
            camera_decision = Decision.OK

        return camera_decision
