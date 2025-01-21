from fastapi import FastAPI

from edge_orchestrator.application.router import router


def create_app() -> FastAPI:
    app = FastAPI(title="edge_orchestrator")
    app.include_router(router)
    return app
