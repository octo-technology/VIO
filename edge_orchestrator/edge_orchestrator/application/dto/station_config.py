from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List

from pydantic import BaseModel

from edge_orchestrator.application.dto.binary_storage_config import BinaryStorageConfig
from edge_orchestrator.application.dto.camera_config import CameraConfig, CameraLogic
from edge_orchestrator.application.dto.edge_station_config import ItemRule
from edge_orchestrator.application.dto.metadata_storage_config import MetadataStorageConfig
from edge_orchestrator.application.dto.model_forward_config import ModelForwardConfig
from edge_orchestrator.application.dto.telemetry_sink_config import TelemetrySinkDto


class InfrastructureConfig(BaseModel):
    binary_storage: BinaryStorageConfig
    metadata_storage: MetadataStorageConfig
    mode1_forward: ModelForwardConfig
    telemetry_sink: TelemetrySinkDto
    cameras: List[CameraConfig]


class DomainRulesConfig(BaseModel):
    camera_rules: List[CameraLogic]
    item_rule: ItemRule = ItemRule()


class StationConfig(BaseModel):
    infra_config: Optional[InfrastructureConfig]
    domain_config: Optional[DomainRulesConfig]

    def to_model(self):
        print(self)
        return

    @staticmethod
    def _prepare_infra(payload: Dict[str, Any]) -> InfrastructureConfig:
        _infra_payload = payload.get("infra", {})
        if not _infra_payload:
            logging.info("No infra logic defined in the config file. Default infra logic will be used.")
            _infra_payload = {"binary_storage": BinaryStorageConfig(), "metadata_storage": MetadataStorageConfig(),
                              "mode1_forward": ModelForwardConfig(), "telemetry": TelemetrySinkDto(),
                              "cameras": [CameraConfig()]}
        return InfrastructureConfig(**_infra_payload)

    @staticmethod
    def _prepare_domain_rules(payload: Dict[str, Any]) -> DomainRulesConfig:
        _domain_rules_payload = payload.get("domain", {})
        if not _domain_rules_payload:
            logging.info("No domain logic defined in the config file. Default domain logic will be used.")
            _domain_rules_payload = {"camera_rules": [CameraLogic()], "item_rule": ItemRule()}
        return DomainRulesConfig(**_domain_rules_payload)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> StationConfig:
        return StationConfig(infra_config=cls._prepare_infra(payload),
                             domain_config=cls._prepare_domain_rules(payload))
