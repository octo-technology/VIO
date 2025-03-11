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


@app.post("/v1/models/{model_name}/versions/{model_version}:predict")
async def predict(model_name: str, payload: JSONStructure, request: Request):
    interpreters = request.app.state.model_interpreters
    if model_name not in interpreters:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    interpreter = request.app.state.model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_dtype = input_details[0]["dtype"] # -> quantization (quantification) of the weights
    input_shape = input_details[0]["shape"] # -> resize input data

    input_data = payload["inputs"]
    input_array = np.array(input_data, dtype=input_dtype)

    interpreter.set_tensor(input_details[0]["index"], input_array)
    interpreter.invoke()

    scores = interpreter.get_tensor(output_details[0]["index"])
    logging.info(f"Scores of classification: {scores[0]}")

    return {"outputs": scores.tolist()}
