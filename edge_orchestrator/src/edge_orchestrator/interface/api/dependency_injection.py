from fastapi import Depends, HTTPException

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_factory import (
    IBinaryStorageFactory,
)
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.camera.i_camera_manager import ICameraManager
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_factory import (
    ICameraRuleFactory,
)
from edge_orchestrator.domain.ports.camera_rule.i_camera_rule_manager import (
    ICameraRuleManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_factory import (
    IMetadataStorageFactory,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_factory import (
    IModelForwarderFactory,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_manager import (
    IModelForwarderManager,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.binary_storage_factory import (
    BinaryStorageFactory,
)
from edge_orchestrator.infrastructure.adapters.binary_storage.binary_storage_manager import (
    BinaryStorageManager,
)
from edge_orchestrator.infrastructure.adapters.camera.camera_factory import (
    CameraFactory,
)
from edge_orchestrator.infrastructure.adapters.camera.camera_manager import (
    CameraManager,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.camera_rule_factory import (
    CameraRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.camera_rule.camera_rule_manager import (
    CameraRuleManager,
)
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_factory import (
    ItemRuleFactory,
)
from edge_orchestrator.infrastructure.adapters.item_rule.item_rule_manager import (
    ItemRuleManager,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.metadata_storage_factory import (
    MetadataStorageFactory,
)
from edge_orchestrator.infrastructure.adapters.metadata_storage.metadata_storage_manager import (
    MetadataStorageManager,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import (
    ModelForwarderFactory,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_manager import (
    ModelForwarderManager,
)


def get_metadata_storage_factory() -> IMetadataStorageFactory:
    return MetadataStorageFactory()


def get_binary_storage_factory() -> IBinaryStorageFactory:
    return BinaryStorageFactory()


def get_model_forwarder_factory() -> IModelForwarderFactory:
    return ModelForwarderFactory()


def get_camera_rule_factory() -> ICameraRuleFactory:
    return CameraRuleFactory()


def get_metadata_storage_manager(
    metadata_storage_factory=Depends(get_metadata_storage_factory),
) -> IMetadataStorageManager:
    return MetadataStorageManager(metadata_storage_factory)


def get_binary_storage_manager(
    binary_storage_factory=Depends(get_binary_storage_factory),
) -> IBinaryStorageManager:
    return BinaryStorageManager(binary_storage_factory)


def get_model_forwarder_manager(
    model_forwarder_factory=Depends(get_model_forwarder_factory),
) -> IModelForwarderManager:
    return ModelForwarderManager(model_forwarder_factory)


def get_camera_rule_manager(camera_rule_factory=Depends(get_camera_rule_factory)) -> ICameraRuleManager:
    return CameraRuleManager(camera_rule_factory)


def get_item_rule_manager() -> ItemRuleManager:
    return ItemRuleManager(ItemRuleFactory())


def get_camera_manager() -> ICameraManager:
    return CameraManager(camera_factory=CameraFactory())


def get_config() -> StationConfig:
    manager = ConfigManager()
    config = manager.get_config()
    if not config:
        raise HTTPException(status_code=400, detail="No active configuration set")
    return config


def get_supervisor(
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    model_forwarder_manager: IModelForwarderManager = Depends(get_model_forwarder_manager),
    camera_rule_manager: ICameraRuleManager = Depends(get_camera_rule_manager),
    item_rule_manager: ItemRuleManager = Depends(get_item_rule_manager),
    camera_manager: ICameraManager = Depends(get_camera_manager),
    station_config: StationConfig = Depends(get_config),
) -> Supervisor:
    supervisor = Supervisor(
        station_config,
        metadata_storage_manager,
        binary_storage_manager,
        model_forwarder_manager,
        camera_rule_manager,
        item_rule_manager,
        camera_manager,
    )
    supervisor._camera_manager.create_cameras(station_config)
    return supervisor
