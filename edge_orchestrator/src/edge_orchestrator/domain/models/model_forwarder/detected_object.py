from typing import Annotated, List, Optional

from pydantic import AfterValidator, BaseModel, Field

from edge_orchestrator.domain.models.validators import round_float, round_float_list


class DetectedObject(BaseModel):
    location: Annotated[List[float], AfterValidator(round_float_list)] = Field(..., min_length=4, max_length=4)
    objectness: Annotated[float, AfterValidator(round_float)]
    label: Optional[str] = None
