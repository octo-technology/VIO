from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from tflite_serving.api_routes import api_router
from tflite_serving.tflite_interpreter import create_model_interpreters


def server() -> FastAPI:
    app = FastAPI(title="tflite_server")
    app.include_router(api_router, prefix="/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.model_interpreters = create_model_interpreters()
    return app


app = server()
