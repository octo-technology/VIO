from enum import Enum


class ItemState(str, Enum):
    TRIGGER = "TRIGGER"
    CAPTURE = "CAPTURE"
    SAVE_BINARIES = "SAVE BINARIES"
    INFERENCE = "INFERENCE"
    CAMERA_RULE = "CAMERA RULE"
    ITEM_RULE = "ITEM RULE"
    DONE = "DONE"
