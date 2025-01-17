import io
from pydantic import BaseModel


class CameraData(BaseModel):
    camera_name: str
    picture: io.BytesIO
    prediction_type: str