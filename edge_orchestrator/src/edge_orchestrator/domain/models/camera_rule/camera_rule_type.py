from enum import Enum


class CameraRuleType(Enum):
    EXPECTED_LABEL_RULE = "expected_label_rule"
    UNEXPECTED_LABEL_RULE = "unexpected_label_rule"
    MIN_NB_OBJECTS_RULE = "min_nb_objects_rule"
    MAX_NB_OBJECTS_RULE = "max_nb_objects_rule"
