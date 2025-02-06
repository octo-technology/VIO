import logging

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule import ICameraRule
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_factory import (
    ICameraRuleFactory,
)
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_manager import (
    ICameraRuleManager,
)


class NoCameraRuleAvailableError(Exception):
    pass


class CameraRuleManager(ICameraRuleManager):
    def __init__(self, camera_rule_factory: ICameraRuleFactory):
        self._camera_rule_factory = camera_rule_factory
        self._camera_rules = {}
        self._logger = logging.getLogger(__name__)

    def _get_camera_rule(self, camera_rule_config: CameraRuleConfig) -> ICameraRule:
        camera_rule_type = camera_rule_config.camera_rule_type
        if camera_rule_type not in self._camera_rules or camera_rule_config.recreate_me:
            camera_rule = self._camera_rule_factory.create_camera_rule(camera_rule_config)
            self._camera_rules[camera_rule_type] = camera_rule
        return self._camera_rules[camera_rule_type]

    def apply_camera_rules(self, item: Item):
        # if self._camera_rules is None or len(self._camera_rules) == 0:
        #     raise NoCameraRuleAvailableError("No camera rule available to apply for each camera!")

        for camera_id, camera_config in item.cameras_metadata.items():
            camera_rule_config: CameraRuleConfig = camera_config.camera_rule_config
            camera_rule = self._get_camera_rule(camera_rule_config)
            item.camera_decisions[camera_id] = camera_rule.apply_camera_rule(item.predictions[camera_id])
