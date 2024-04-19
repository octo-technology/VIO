from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from hub_labelizer.application import settings
from hub_labelizer.application.trigger_routes import trigger_router


def server() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(trigger_router, prefix=settings.url_prefix)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
