from typing import Dict, Union

from edge_orchestrator.domain.models.business_rule.camera_rule.camera_rule import (
    CameraRule,
)
from edge_orchestrator.domain.models.decision import Decision


class ExpectedLabelRule(CameraRule):
    def __init__(self, expected_label: str):
        self.expected_label = expected_label

    def get_camera_decision(self, inference: Dict[str, Union[str, Dict]]) -> Decision:
        if len(inference) == 0:
            return Decision.KO

        for inf in inference:
            if inf in self.expected_label:
                camera_decision = Decision.OK
            else:
                camera_decision = Decision.KO

        return camera_decision
