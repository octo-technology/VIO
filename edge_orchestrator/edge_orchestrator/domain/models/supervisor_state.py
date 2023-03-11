from enum import Enum


class SupervisorState(Enum):
    CAPTURE = "Capture"
    SAVE_BINARIES = "Save Binaries"
    INFERENCE = "Inference"
    DECISION = "Decision"
    DONE = "Done"
