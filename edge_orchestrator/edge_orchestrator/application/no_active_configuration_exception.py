from fastapi import Request
from fastapi.responses import JSONResponse


class NoActiveConfigurationException(Exception):
    def __init__(self, name: str):
        self.name = name


async def no_active_configuration_exception_handler(
    request: Request, exc: NoActiveConfigurationException
):
    return JSONResponse(
        status_code=403,
        content={
            "message": f"No active configuration selected: {exc.name}! "
            "Set the active station configuration before triggering the inspection or the upload."
        },
    )
