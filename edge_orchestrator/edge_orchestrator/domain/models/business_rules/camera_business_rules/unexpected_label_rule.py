from typing import Dict, Union

from edge_orchestrator.domain.models.business_rules.camera_rule import CameraRule
from edge_orchestrator.domain.models.decision import Decision


class UnexpectedLabelRule(CameraRule):
    def __init__(self, unexpected_label: str):
        self.unexpected_label = unexpected_label

    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        camera_decision = Decision.OK
        for inf in inference:
            if inf in self.unexpected_label:
                camera_decision = Decision.KO
        return camera_decision
