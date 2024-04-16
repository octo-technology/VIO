import datetime as dt
import uuid

from typing import Dict, Type, List



def generate_id() -> str:
    return str(uuid.uuid4())


class Item:
    def __init__(
        self,
        serial_number: str,
        category: str,
        cameras_metadata: Dict[str, Dict],
        binaries: Dict[str, bytes],
        dimensions: Dict[str, List[int]],
    ):
        self.id = generate_id()
        self.received_time = dt.datetime.now()
        self.serial_number = serial_number
        self.category = category
        self.cameras_metadata = cameras_metadata
        self.binaries = binaries
        self.dimensions = dimensions

        self.inferences = {}
        self.decision = {}
        self.state = None
        self.error = None
        self.error_message = None
        self.station_config = None

    @classmethod
    def from_nothing(cls):
        return Item("serial_number", "category", {}, {}, {})

    def get_metadata(self, with_id: bool = True) -> Dict:
        metadata = {
            "serial_number": self.serial_number,
            "category": self.category,
            "station_config": self.station_config,
            "cameras": self.cameras_metadata,
            "received_time": self.received_time.strftime("%Y-%m-%d %H:%M:%S"),
            "dimensions": self.dimensions,
            "inferences": self.inferences,
            "decision": self.decision,
            "state": self.state,
            "error": self.error_message,
        }
        if with_id:
            metadata["id"] = self.id
        return metadata

    def __eq__(self, other) -> bool:
        return (
            self.id == other.id
            and self.received_time == other.received_time
            and self.serial_number == other.serial_number
            and self.category == other.category
            and self.cameras_metadata == other.cameras_metadata
            and self.binaries == other.binaries
            and self.dimensions == other.dimensions
            and self.inferences == other.inferences
            and self.decision == other.decision
            and self.state == other.state
        )
