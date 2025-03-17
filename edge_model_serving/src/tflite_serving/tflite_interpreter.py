import logging
import os
from pathlib import Path
from typing import Dict



# JE SUIS DANS LE SERVICE EDGE_MODEL_SERVING POUR SERVIR LES MODELS


def create_interpreter(model_path: Path) -> Interpreter:
    # Je charge le modèle
    


    logging.info(f"Loaded model {model_path.parent.name} from {model_path.resolve()}")
    return interpreter


def create_model_interpreters() -> Dict[str, Interpreter]:
    model_interpreters = {}
    models_path = (
        Path(os.getenv("MODELS_PATH"))
        if os.getenv("MODELS_PATH")
        else Path.cwd() / "models"
    )
    tflite_model_path = models_path / "tflite"
    logging.info(f"tflite_model_path: {tflite_model_path.resolve()}")
    
    for model_path in tflite_model_path.glob("**/*.tflite"):
        model_interpreters[model_path.parent.name] = create_interpreter(model_path)
    return model_interpreters
