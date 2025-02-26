from enum import Enum


class Decision(str, Enum):
    KO = "KO"
    OK = "OK"
    NO_DECISION = "NO_DECISION"
