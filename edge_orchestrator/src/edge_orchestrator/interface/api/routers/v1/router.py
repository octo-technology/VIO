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
    get_metadata_storage_factory,
    get_data_gathering,
    get_metadata_storage_manager,
    get_supervisor,
)


def home():
    return "the edge orchestrator is up and running"


def get_health():
    return {"status": "ok"}


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


def get_all_configs(reload: Optional[bool] = False) -> Dict[str, StationConfig]:
    manager = ConfigManager()
    if reload:
        manager.reload_configs()
    configs = manager.all_configs
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
) -> List[str]:
    binary_storage = binary_storage_manager.get_binary_storage(station_config)
    return binary_storage.get_item_binary_names(item_id)


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


async def upload_job(
    class_name: Optional[str] = None,
    binaries: List[UploadFile] = [],
    cameras_metadata: Dict[str, CameraConfig] = {},
    data_gathering: DataGathering = Depends(get_data_gathering),
    station_config: StationConfig = Depends(get_config),
    background_tasks: BackgroundTasks = None,
):
    # Set the class name on the config
    if class_name is None:
        class_name = "NA"
    station_config.binary_storage_config.class_directory = class_name
    station_config.metadata_storage_config.class_directory = class_name

    items = []
    for binary in binaries:
        background_tasks.add_task(
            data_gathering.upload,
            Item(
                cameras_metadata=cameras_metadata,
                binaries={binary.filename: Image(image_bytes=await binary.read())},
            ),
            station_config,
        )
    return {"items_ids": [item.id for item in items]}


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
router.add_api_route("/configs/active", set_config, methods=["POST"], response_model_exclude_none=True)

router.add_api_route("/trigger", trigger_job, methods=["POST"])
router.add_api_route("/data_gathering", data_gathering_job, methods=["POST"])
router.add_api_route("/upload", upload_job, methods=["POST"])
