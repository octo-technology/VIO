from enum import Enum
from typing import Optional, List

import annotated_types
from pydantic import (
    StringConstraints,
    BaseModel,
    FilePath,
    PositiveInt,
    Field,
    model_validator,
)
from typing_extensions import Annotated


class ModelNameEnum(str, Enum):
    inception = "inception"
    mask_classification_model = "mask_classification_model"
    marker_quality_control = "marker_quality_control"
    mobilenet_v1_640x640 = "mobilenet_v1_640x640"
    mobilenet_ssd_v2_coco = "mobilenet_ssd_v2_coco"
    mobilenet_ssd_v2_face = "mobilenet_ssd_v2_face"
    cellphone_connection_control = "cellphone_connection_control"


class ModelCategoryEnum(str, Enum):
    classification = "classification"
    object_detection = "object_detection"


Version = Annotated[
    str,
    StringConstraints(pattern=r"^(0|[1-9]\d*)(\.(0|[1-9]\d*)){0,2}"),
]


class ModelOutput(BaseModel):
    boxes_coordinates: str
    objectness_scores: str
    number_of_boxes: Optional[str] = None
    detection_classes: str


class ModelConfig(BaseModel):
    name: ModelNameEnum
    category: ModelCategoryEnum
    version: Version
    class_names: Optional[List[str]] = None
    class_names_path: Optional[FilePath] = None
    output: Optional[ModelOutput] = None
    image_resolution: List[PositiveInt] = Field(min_items=2, max_items=2)
    objectness_threshold: Optional[
        Annotated[float, annotated_types.Interval(gt=0, le=1.0)]
    ] = None
    depends_on: Optional[List[str]] = None
    class_to_detect: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_class_names_or_class_names_path(self) -> "ModelConfig":
        if (not self.class_names and not self.class_names_path) or (
            self.class_names and self.class_names_path
        ):
            raise ValueError(
                "Either class_names or class_names_path is required (not both)"
            )
        return self

    @model_validator(mode="after")
    def check_object_detection_model(self) -> "ModelConfig":
        if self.category is ModelCategoryEnum.object_detection:
            if not self.output:
                raise ValueError("output is required with object_detection category")
            if not self.objectness_threshold:
                raise ValueError(
                    "objectness_threshold is required with object_detection category"
                )
            if not self.class_to_detect:
                raise ValueError(
                    "class_to_detect is required with object_detection category"
                )
        return self
