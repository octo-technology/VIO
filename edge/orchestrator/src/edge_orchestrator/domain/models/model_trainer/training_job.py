from typing import Optional

from pydantic import BaseModel


class TrainingJob(BaseModel):
    """Progress of a memory-bank fit running on a model-serving backend.

    Mirrors the fields the anomaly-serving service reports so the orchestrator
    can proxy a job straight through to the dashboard, adding nothing of its own.
    """

    job_id: str
    model_name: str
    status: str
    total: int
    processed: int = 0
    bank_size: Optional[int] = None
    error: Optional[str] = None
