from typing import Dict, List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    UploadFile,
)

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.binary_storage.i_binary_storage_manager import (
    IBinaryStorageManager,
)
from edge_orchestrator.domain.ports.metadata_storage.i_metadata_storage_manager import (
    IMetadataStorageManager,
)
from edge_orchestrator.interface.api.dependency_injection import (
    get_binary_storage_manager,
    get_config,
    get_metadata_storage_manager,
    get_supervisor,
)


def home():
    return "the edge orchestrator is up and running"


def get_health():
    return {"status": "ok"}


def set_config(station_name: Optional[str] = None, station_config: Optional[StationConfig] = None):
    if (station_name and station_config) or (station_name is None and station_config is None):
        raise HTTPException(status_code=422, detail="Either provide a station_name or a StationConfig (exclusive)")

    manager = ConfigManager()
    if station_name:
        manager.set_config_by_name(station_name)
        return {"message": f"Configuration set successfully as {station_name}"}
    if station_config:
        manager.set_config(station_config)
        return {"message": f"Configuration updated successfully with {station_config.station_name}"}


def get_all_configs() -> Dict[str, StationConfig]:
    manager = ConfigManager()
    configs = manager.get_all_configs()
    if not configs:
        raise HTTPException(status_code=400, detail="No existing configuration")
    return configs


def get_all_items_metadata(
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> List[Item]:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_all_items_metadata()


def get_item_metadata(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> Item:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id)


def get_item_binaries(
    item_id: UUID,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> Dict[str, bytes]:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return binary_storage.get_item_binaries(item_id)


def get_item_binary(
    item_id: UUID,
    camera_id: str,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> bytes:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return Response(content=binary_storage.get_item_binary(item_id, camera_id), media_type="image/jpeg")


def get_item_state(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> ItemState:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id).state


async def trigger_job(
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    supervisor: Supervisor = Depends(get_supervisor),
    background_tasks: BackgroundTasks = None,
):
    input_binaries = {}
    for binary in binaries:
        input_binaries[binary.filename] = Image(image_bytes=binary.read())
    item = Item(
        cameras_metadata=cameras_metadata,
        binaries=input_binaries,
    )
    background_tasks.add_task(supervisor.inspect, item)
    return {"item_id": item.id}


router = APIRouter(prefix="/api/v1")
router.add_api_route("/", home, methods=["GET"])
router.add_api_route("/health/live", get_health, methods=["GET"])
router.add_api_route("/items", get_all_items_metadata, methods=["GET"], response_model_exclude_none=True)
router.add_api_route("/items/{item_id}", get_item_metadata, methods=["GET"], response_model_exclude_none=True)
router.add_api_route("/items/{item_id}/binaries/{camera_id}", get_item_binary, methods=["GET"])
router.add_api_route("/items/{item_id}/binaries", get_item_binaries, methods=["GET"])
router.add_api_route("/items/{item_id}/state", get_item_state, methods=["GET"], response_model_exclude_none=True)
router.add_api_route("/configs", get_all_configs, methods=["GET"], response_model_exclude_none=True)
router.add_api_route("/configs/active", get_config, methods=["GET"], response_model_exclude_none=True)
router.add_api_route("/configs/active/{station_name}", set_config, methods=["POST"])

router.add_api_route("/trigger_job", trigger_job, methods=["POST"])
