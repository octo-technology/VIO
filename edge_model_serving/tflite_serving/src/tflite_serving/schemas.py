from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel


class DetectedObject(BaseModel):
    location: List[float]
    objectness: float
    label: str
    severity: Optional[float] = None


class ClassificationPrediction(BaseModel):
    prediction_type: Literal["class"]
    label: str
    probability: float


class DetectionPrediction(BaseModel):
    prediction_type: Literal["objects"]
    detected_objects: Dict[str, DetectedObject]


PredictionResponse = Union[ClassificationPrediction, DetectionPrediction]


class ModelMetadataResponse(BaseModel):
    input_shape: List[int]
    input_dtype: str
    output_type: Optional[str] = None
    class_names: Optional[List[str]] = None
    normalization: Optional[str] = None
