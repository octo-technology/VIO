from typing import Dict, Union

from edge_orchestrator.domain.models.business_rule.camera_rule.camera_rule import (
    CameraRule,
)
from edge_orchestrator.domain.models.decision import Decision


class MaxNbObjectsRule(CameraRule):
    def __init__(self, class_to_detect: str, max_threshold: int):
        self.class_to_detect = class_to_detect
        self.max_threshold = max_threshold

    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        objects_of_interest = [obj for obj in inference if obj in self.class_to_detect]

        if len(objects_of_interest) < self.max_threshold:
            camera_decision = Decision.KO
        else:
            camera_decision = Decision.OK

        return camera_decision
