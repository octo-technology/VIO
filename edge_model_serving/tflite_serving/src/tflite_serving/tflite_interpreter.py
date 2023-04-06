import os
from pathlib import Path
from typing import Dict

from tflite_runtime.interpreter import Interpreter


def create_interpreter(model_path: str) -> Interpreter:
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def create_model_interpreters() -> Dict[str, Interpreter]:
    model_interpreters = {}
    models_path = Path(os.getenv("MODELS_PATH")) if os.getenv("MODELS_PATH") else Path.cwd().parent
    tflite_model_path = models_path / 'tflite'
    for model_path in tflite_model_path.glob('**/*.tflite'):
        model_interpreters[model_path.parent.name] = create_interpreter(model_path.as_posix())
    return model_interpreters
