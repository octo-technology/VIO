import logging
import os
from pathlib import Path
from typing import Any, AnyStr, Dict, List, Union

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware

from tflite_serving.tflite_interpreter import create_model_interpreters

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - %(asctime)s - %(name)s - %(message)s"
)
app = FastAPI(title="edge_model_server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
models_path = Path(os.getenv("MODELS_PATH", "models/"))
assert models_path.exists(), f"Models path does not exist at {models_path.resolve()}"
app.state.model_interpreters = create_model_interpreters()


@app.get("/")
def home():
    return {"Hello": "From edge_model_server"}


# JE SUIS DANS LE SERVICE EDGE_MODEL_SERVING POUR SERVIR LES MODELS

@app.post("/v1/models/{model_name}/versions/{model_version}:predict")
async def predict(model_name: str, payload: JSONStructure, request: Request):
    interpreters = request.app.state.model_interpreters
    if model_name not in interpreters:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    # Je récupère l'interpreter de mon modèle
    

    # je récupère les détails de l'input et de l'output
    


    # je récupère le type et la taille de l'input attendu
    
    

    input_data = payload["inputs"]
    # input_array = np.array(input_data, dtype=input_dtype)

    # je mets mon image dans la zone mémoire allouée pour prédire
    

    # je prédis
    

    # je récupère les scores de classification
    # scores = 
    logging.info(f"Scores of classification: {scores[0]}")

    return {"outputs": scores.tolist()}
