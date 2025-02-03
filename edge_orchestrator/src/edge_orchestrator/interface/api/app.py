import logging

from fastapi import FastAPI

from edge_orchestrator.interface.api.router import router


def create_app() -> FastAPI:
    logging.getLogger().setLevel(logging.INFO)
    app = FastAPI(title="edge_orchestrator")
    app.include_router(router)
    return app
