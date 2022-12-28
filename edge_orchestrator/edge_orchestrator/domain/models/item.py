import datetime as dt
import uuid
from typing import Dict, Type

from edge_orchestrator.domain.models.business_rules.item_business_rule.item_threshold_ratio_rule import ThresholdRatioRule
from edge_orchestrator.domain.models.business_rules.item_business_rule.item_threshold_rule import ThresholdRule
from edge_orchestrator.domain.models.business_rules.item_rule import ItemRule


def generate_id():
    return str(uuid.uuid4())


def get_item_rule(item_rule_name) -> Type[ItemRule]:
    if item_rule_name == 'threshold_ratio_rule':
        return ThresholdRatioRule

    elif item_rule_name == 'min_threshold_KO_rule':
        return ThresholdRule
    else:
        raise NotImplementedError


class Item:
    def __init__(self, serial_number: str, category: str, cameras_metadata: Dict[str, Dict],
                 binaries: Dict[str, bytes]):
        self.id = generate_id()
        self.received_time = dt.datetime.now()
        self.serial_number = serial_number
        self.category = category
        self.cameras_metadata = cameras_metadata
        self.binaries = binaries

        self.inferences = {}
        self.decision = {}
        self.state = None
        self.error = None
        self.error_message = None
        self.station_config = None

    @classmethod
    def from_nothing(cls):
        return Item('serial_number', 'category', {}, {})

    def get_metadata(self) -> Dict:
        return {
            'serial_number': self.serial_number,
            'category': self.category,
            'station_config': self.station_config,
            'cameras': self.cameras_metadata,
            'received_time': self.received_time.strftime('%Y-%m-%d %H:%M:%S'),
            'inferences': self.inferences,
            'decision': self.decision,
            'state': self.state
        }

    def __eq__(self, other) -> bool:
        return (self.id == other.id and self.received_time == other.received_time and
                self.serial_number == other.serial_number and self.category == other.category and
                self.cameras_metadata == other.cameras_metadata and self.binaries == other.binaries and
                self.inferences == other.inferences and self.decision == other.decision and self.state == other.state)
