from pydantic.main import BaseModel


class StationConfigDto(BaseModel):
    config_name: str = "config_name"
