from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_state import ItemState


class IItemRule(ABC):
    _item_rule_config: ItemRuleConfig
    _logger: Logger

    @abstractmethod
    def _get_item_decision(self, camera_decisions: Dict[str, Decision]) -> Decision:
        pass

    def apply_item_rules(self, item: Item):
        self._logger.info("Applying rule on item...")

        if len(item.camera_decisions) == 0:
            self._logger.warning(f"Item {item.id} has no camera decisions, setting decision to NO_DECISION")
            item.decision = Decision.NO_DECISION
        else:
            item.decision = self._get_item_decision(item.camera_decisions)
            self._logger.info(f"Item rule applied for item {item.id}!")
        item.state = ItemState.ITEM_RULE
