import json
import logging
import os
from pathlib import Path
from typing import Dict

from ai_edge_litert.interpreter import Interpreter


def create_interpreter(model_path: Path) -> Interpreter:
    interpreter = Interpreter(model_path=model_path.as_posix())
    interpreter.allocate_tensors()
    logging.info(f"Loaded model {model_path.parent.name} from {model_path.resolve()}")
    return interpreter


def load_model_metadata(model_dir: Path) -> dict:
    metadata_path = model_dir / "metadata.json"
    if not metadata_path.exists():
        logging.warning(f"No metadata.json found for model at {model_dir}. Serving will use heuristics.")
        return {}
    with metadata_path.open() as f:
        return json.load(f)


def _get_tflite_model_path() -> Path:
    models_path = Path(os.getenv("MODELS_PATH")) if os.getenv("MODELS_PATH") else Path.cwd().parent / "models"
    return models_path / "tflite"


def create_model_interpreters() -> Dict[str, Interpreter]:
    model_interpreters = {}
    tflite_model_path = _get_tflite_model_path()
    logging.info(f"tflite_model_path: {tflite_model_path.resolve()}")
    for model_path in tflite_model_path.glob("**/*.tflite"):
        model_interpreters[model_path.parent.name] = create_interpreter(model_path)
    return model_interpreters


def create_model_metadata_registry() -> Dict[str, dict]:
    registry = {}
    tflite_model_path = _get_tflite_model_path()
    if not tflite_model_path.exists():
        return registry
    for model_dir in tflite_model_path.iterdir():
        if model_dir.is_dir():
            registry[model_dir.name] = load_model_metadata(model_dir)
    return registry
