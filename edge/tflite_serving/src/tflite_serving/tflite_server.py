import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from tflite_serving.api_routes import api_router
from tflite_serving.tflite_interpreter import (
    create_model_interpreters,
    create_model_metadata_registry,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not getattr(app.state, "model_interpreters", None):
        try:
            app.state.model_interpreters = create_model_interpreters()
            app.state.model_metadata = create_model_metadata_registry()
        except Exception:
            logging.exception("Failed to load models — server will return 503 on model routes")
            app.state.model_interpreters = None
            app.state.model_metadata = None
    yield
    app.state.model_interpreters = None
    app.state.model_metadata = None


def server() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(asctime)s - %(message)s")
    app = FastAPI(title="tflite_server", lifespan=lifespan)
    app.include_router(api_router, prefix="/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = server()
