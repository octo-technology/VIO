import os

URL_ORCH = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/v1/")

URL_CONFIGS = URL_ORCH + "configs"
URL_ACTIVE_CONFIG = URL_ORCH + "configs/active"
