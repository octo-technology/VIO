import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from anomaly_serving.api_routes import api_router
from anomaly_serving.fit_jobs import init_job_state
from anomaly_serving.rad_registry import (
    create_model_metadata_registry,
    create_model_registry,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_job_state(app)
    if not getattr(app.state, "rad_models", None):
        try:
            # Loading here rather than per-request keeps the encoder download and
            # the memory-bank upload off the inference path.
            app.state.rad_models = create_model_registry()
            app.state.model_metadata = create_model_metadata_registry()
        except Exception:
            logging.exception("Failed to load models — server will return 503 on model routes")
            app.state.rad_models = None
            app.state.model_metadata = None
    yield
    app.state.rad_models = None
    app.state.model_metadata = None


def server() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(asctime)s - %(message)s")
    app = FastAPI(title="anomaly_server", lifespan=lifespan)
    app.include_router(api_router, prefix="/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = server()
