from typing import Annotated, List, Optional

from pydantic import AfterValidator, BaseModel, Field


def round_float(value: float) -> float:
    return round(value, 5)


def round_float_list(values: List[float]) -> List[float]:
    return [round(value, 5) for value in values]


class DetectedObject(BaseModel):
    location: Annotated[List[float], AfterValidator(round_float_list)] = Field(..., min_length=4, max_length=4)
    objectness: Annotated[float, AfterValidator(round_float)]
    label: Optional[str] = None
