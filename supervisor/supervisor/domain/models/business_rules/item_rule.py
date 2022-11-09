from typing import Dict

from abc import ABC, abstractmethod
from supervisor.domain.models.decision import Decision


class ItemRule(ABC):

    @abstractmethod
    def get_item_decision(self, cameras_decisions: Dict[str, str]) -> Decision:
        pass
