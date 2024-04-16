import os

from hub_labelizer import logger
from hub_labelizer.environment.config import Config

from hub_labelizer.infrastructure.labelizer.labelbox_labelizer import (
    LabelboxLabelizer
)


class Default(Config):
    os.environ["ORCHESTRATOR_MODEL_URL"] = "http://0.0.0.0:8000"
    ORCHESTRATOR_MODEL_URL = os.environ.get(
        "ORCHESTRATOR_MODEL_URL", "http://0.0.0.0:8000"
    )

    def __init__(self):
        self.url = self.ORCHESTRATOR_MODEL_URL
        self.labelizer = LabelboxLabelizer()

        self.metadata_storage = None
        self.binary_storage = None
        self.station_config = None
