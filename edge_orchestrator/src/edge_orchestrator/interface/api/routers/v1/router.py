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
from edge_orchestrator.application.use_cases.data_gathering import DataGathering
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.image import Image
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
    get_data_gathering,
    get_metadata_storage_manager,
    get_supervisor,
)

router = APIRouter(prefix="/api/v1")
router.add_api_route("/configs/active", get_config, methods=["GET"], response_model_exclude_none=True)


@router.get("/")
def home():
    return "the edge orchestrator is up and running"


@router.get("/health/live")
def get_health():
    return {"status": "ok"}


@router.post("/configs/active", response_model=StationConfig, response_model_exclude_none=True)
def set_config(
    station_name: Optional[str] = None,
    station_config: Optional[StationConfig] = None,
) -> StationConfig:
    if (station_name and station_config) or (station_name is None and station_config is None):
        raise HTTPException(status_code=422, detail="Either provide a station_name or a StationConfig (exclusive)")

    manager = ConfigManager()
    if station_name:
        manager.set_config_by_name(station_name)
    if station_config:
        manager.set_config(station_config)
    return manager.get_config()


@router.get("/configs", response_model=Dict[str, StationConfig], response_model_exclude_none=True)
def get_all_configs(reload: Optional[bool] = False) -> Dict[str, StationConfig]:
    manager = ConfigManager()
    if reload:
        manager.reload_configs()
    configs = manager.all_configs
    if not configs:
        raise HTTPException(status_code=400, detail="No existing configuration")
    return configs


@router.get("/items", response_model=List[Item], response_model_exclude_none=True)
def get_all_items_metadata(
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> List[Item]:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_all_items_metadata()


@router.get("/items/{item_id}", response_model=Item, response_model_exclude_none=True)
def get_item_metadata(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> Item:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id)


@router.get("/items/{item_id}/binaries", response_model=List[str])
def get_item_binaries(
    item_id: UUID,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> List[str]:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return binary_storage.get_item_binary_names(item_id)


@router.get("/items/{item_id}/binaries/{camera_id}", response_model=bytes)
def get_item_binary(
    item_id: UUID,
    camera_id: str,
    binary_storage_manager: IBinaryStorageManager = Depends(get_binary_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> bytes:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return Response(content=binary_storage.get_item_binary(item_id, camera_id), media_type="image/jpeg")


@router.get("/items/{item_id}/state", response_model=ItemState, response_model_exclude_none=True)
def get_item_state(
    item_id: UUID,
    metadata_storage_manager: IMetadataStorageManager = Depends(get_metadata_storage_manager),
    station_config: StationConfig = Depends(get_config),
) -> ItemState:
    metadata_storage = metadata_storage_manager.get_metadata_storage(station_config)
    return metadata_storage.get_item_metadata(item_id).state


@router.post("/trigger", response_model=Dict[str, UUID])
async def trigger_job(
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    supervisor: Supervisor = Depends(get_supervisor),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    input_binaries = {}
    for binary in binaries:
        input_binaries[binary.filename] = Image(image_bytes=await binary.read())
    item = Item(
        cameras_metadata=cameras_metadata,
        binaries=input_binaries,
    )
    background_tasks.add_task(supervisor.inspect, item, station_config)
    return {"item_id": item.id}


@router.post("/data_gathering", response_model=Dict[str, UUID])
async def data_gathering_job(
    class_name: str = None,
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    data_gathering: DataGathering = Depends(get_data_gathering),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    # Set the class name on the config
    station_config.binary_storage_config.class_directory = class_name
    station_config.metadata_storage_config.class_directory = class_name

    input_binaries = {}
    for binary in binaries:
        input_binaries[binary.filename] = Image(image_bytes=await binary.read())
    item = Item(
        cameras_metadata=cameras_metadata,
        binaries=input_binaries,
    )
    background_tasks.add_task(data_gathering.acquire, item, station_config)
    return {"item_id": item.id}
