from fastapi import Request
from fastapi.responses import JSONResponse

from edge_orchestrator.domain.exceptions import ConfigNotFoundError, InvalidConfigNameError


async def config_not_found_handler(request: Request, exc: ConfigNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def invalid_config_name_handler(request: Request, exc: InvalidConfigNameError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
