"""Response models for the RAD serving API.

The predict response deliberately reuses the ``"class"`` discriminator and the
``label``/``probability`` field names of ``tflite_serving``'s
``ClassificationPrediction``.  The orchestrator's ``ModelForwarder`` parses a
serving response by that discriminator and reads only those two fields, so a RAD
model drops into an existing pipeline step with no orchestrator change, and the
existing ``expected_label_rule`` camera rule evaluates its OK/KO verdict as-is.
The anomaly-specific fields ride along for clients that know to look for them.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel


class AnomalyPrediction(BaseModel):
    prediction_type: Literal["class"] = "class"
    label: str
    probability: float
    raw_score: float
    decision_method: str
    decision_param: float
    threshold: float


PredictionResponse = AnomalyPrediction


class FitJobAccepted(BaseModel):
    """Returned when a memory-bank fit is accepted and scheduled."""

    job_id: str
    total: int
    status: str


class FitJobStatus(BaseModel):
    """Progress snapshot of a memory-bank fit job."""

    job_id: str
    model_name: str
    status: str
    processed: int
    total: int
    bank_size: Optional[int] = None
    error: Optional[str] = None


class ModelMetadataResponse(BaseModel):
    version: str = "1"
    input_shape: List[int]
    input_dtype: str
    output_type: Optional[str] = None
    class_names: Optional[List[str]] = None
    normalization: Optional[str] = None
    backbone: Optional[str] = None
    resize: Optional[int] = None
    decision_method: Optional[str] = None
    decision_param: Optional[float] = None
    threshold: Optional[float] = None
