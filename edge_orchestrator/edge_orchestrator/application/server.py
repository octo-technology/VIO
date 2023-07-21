from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_orchestrator.application.api_routes import api_router
from edge_orchestrator.application.no_active_configuration_exception import (
    NoActiveConfigurationException,
    no_active_configuration_exception_handler,
)
from edge_orchestrator.application.trigger_routes import trigger_router


def server() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    app.include_router(trigger_router)
    app.add_exception_handler(
        NoActiveConfigurationException, no_active_configuration_exception_handler
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
