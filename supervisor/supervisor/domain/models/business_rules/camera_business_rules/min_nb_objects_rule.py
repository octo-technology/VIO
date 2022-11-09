from typing import Dict, Union

from supervisor.domain.models.decision import Decision
from supervisor.domain.models.business_rules.camera_rule import CameraRule


class MinNbObjectsRule(CameraRule):
    def __init__(self, class_to_detect: str, min_threshold: int):
        self.class_to_detect = class_to_detect
        self.min_threshold = min_threshold

    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:

        objects_of_interest = [obj for obj in inference if obj in self.class_to_detect]

        if len(objects_of_interest) < self.min_threshold:
            camera_decision = Decision.KO
        else:
            camera_decision = Decision.OK

        return camera_decision
