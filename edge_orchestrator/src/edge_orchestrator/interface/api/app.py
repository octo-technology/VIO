import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_orchestrator.interface.api.routers.v1.router import router


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(asctime)s - %(name)s - %(message)s")
    app = FastAPI(title="edge_orchestrator")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
