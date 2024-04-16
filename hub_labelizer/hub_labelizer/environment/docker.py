import os

from hub_labelizer.environment.config import Config

from hub_labelizer.infrastructure.labelizer.labelbox_labelizer import LabelboxLabelizer


class Docker(Config):
    os.environ["EDGE_ORCHESTRATOR_URL"] = "http://edge_orchestrator:8000"
    ORCHESTRATOR_MODEL_URL = os.environ.get(
        "EDGE_ORCHESTRATOR_URL", "http://edge_orchestrator:8000"
    )

    def __init__(self):
        self.url = self.ORCHESTRATOR_MODEL_URL
        self.labelizer = LabelboxLabelizer()
