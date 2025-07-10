import onnxruntime as ort
import os
from pathlib import Path

MODELS_PATH = Path(os.getenv("MODELS_PATH", "/models"))

# chercehr tous les modèles .onnx
model_files = list(MODELS_PATH.rglob("*.onnx"))

if not model_files:
    raise FileNotFoundError(f"Aucun modèle ONNX trouvé dans {MODELS_PATH}")

print(f"Modèles trouvés : {[str(m) for m in model_files]}")

# choisir par défaut le premier modèle onnx disponible
MODEL_PATH = str(model_files[0])

class ONNXModel:
    def __init__(self):
        """Initialiser ONNX Runtime avec tous les modèles trouvés"""
        self.models = {}
        model_files = list(MODELS_PATH.rglob("*.onnx"))
        
        if not model_files:
            raise FileNotFoundError(f"Aucun modèle ONNX trouvé dans {MODELS_PATH}")

        for model_path in model_files:
            model_name = model_path.stem  # Nom du modele sans extension
            self.models[model_name] = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"]) # Création d'une session d'inference par modèle
            print(f"Model {model_name} loaded from {model_path}")




    """"
    def predict(self, model_name, input_array):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")
        
        session = self.models[model_name]
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: input_array})
        return outputs
    """
