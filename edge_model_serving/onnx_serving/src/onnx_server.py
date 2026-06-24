from fastapi import FastAPI
import logging
from api_routes import api_router
from onnx_interpreter import ONNXModel

app = FastAPI()

# Charger les modèles ONNX au démarrage du serveur
@app.on_event("startup")
async def load_model():
    logging.info("Chargement des modèles ONNX...")
    model = ONNXModel()  # Charge tous les modèles
    app.state.model_interpreters = model.models  # stocke tous les modèles 
    logging.info(f"Modèles chargés : {list(model.models.keys())}")

app.include_router(api_router)

# health check du serveur ONNX
@app.get("/")
async def root():
    return {"message": "ONNX Model Serving is running!", "models": list(app.state.model_interpreters.keys())}
