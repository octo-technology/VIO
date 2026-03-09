from fastapi import APIRouter

from edge_orchestrator.interface.api.routers.v1 import configs, health, items, jobs


def home():
    return "the edge orchestrator is up and running"


router = APIRouter(prefix="/api/v1")
router.add_api_route("/", home, methods=["GET"])
router.include_router(health.router)
router.include_router(configs.router)
router.include_router(items.router)
router.include_router(jobs.router)
