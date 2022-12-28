from typing import Dict

from abc import ABC, abstractmethod
from edge_orchestrator.domain.models.decision import Decision


class ItemRule(ABC):

    @abstractmethod
    def get_item_decision(self, cameras_decisions: Dict[str, str]) -> Decision:
        pass
