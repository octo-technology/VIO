import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.data_gathering import DataGathering
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.application.workers.inspection_worker import (
    run_inspection_worker,
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
from edge_orchestrator.infrastructure.adapters.inspection_queue.sqlite_inspection_queue import (
    SqliteInspectionQueue,
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
from edge_orchestrator.interface.api.routers.v1.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    binary_storage_manager = BinaryStorageManager(BinaryStorageFactory())
    metadata_storage_manager = MetadataStorageManager(MetadataStorageFactory())
    model_forwarder_manager = ModelForwarderManager(ModelForwarderFactory())
    camera_rule_manager = CameraRuleManager(CameraRuleFactory())
    item_rule_manager = ItemRuleManager(ItemRuleFactory())
    camera_manager = CameraManager(CameraFactory())

    app.state.binary_storage_manager = binary_storage_manager
    app.state.metadata_storage_manager = metadata_storage_manager
    app.state.supervisor = Supervisor(
        metadata_storage_manager,
        binary_storage_manager,
        model_forwarder_manager,
        camera_rule_manager,
        item_rule_manager,
        camera_manager,
    )
    app.state.data_gathering = DataGathering(
        metadata_storage_manager,
        binary_storage_manager,
        camera_manager,
    )
    app.state.config_manager = ConfigManager()

    db_path = Path(os.getenv("INSPECTION_QUEUE_DB_PATH", "/tmp/vio_inspection_queue.db"))
    inspection_queue = SqliteInspectionQueue(db_path)
    await inspection_queue.initialize()
    app.state.inspection_queue = inspection_queue

    worker_task = asyncio.create_task(
        run_inspection_worker(inspection_queue, app.state.supervisor, app.state.config_manager)
    )

    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    await inspection_queue.close()


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(asctime)s - %(name)s - %(message)s")
    app = FastAPI(title="edge_orchestrator", lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
