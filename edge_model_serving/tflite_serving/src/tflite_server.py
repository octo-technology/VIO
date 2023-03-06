import logging
import os
from pathlib import Path
from typing import Any, AnyStr, Dict, Union, List
import tflite_runtime.interpreter as tflite
from fastapi import FastAPI, HTTPException
import numpy as np

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

app = FastAPI()

coral_tpu = os.environ.get('TPU', 'false')


def create_interpreter(model_directory: Path):
    model_path = str([filepath for filepath in model_directory.iterdir(
    ) if '.tflite' in filepath.name][0])
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


# Create the different interpreters
model_interpreters = {}

model_path = Path.cwd().parent.parent / 'models'

for model_directory in model_path.iterdir():
    if model_directory.is_dir():
        model_interpreters[model_directory.name] = create_interpreter(
            model_directory)


@app.get("/")
async def info():
    return """tflite-server docs at ip:port/docs"""


@app.get("/v1/models")
async def get_models():
    return list(model_interpreters.keys())


@app.get("/v1/models/{model_name}/versions/{model_version}/resolution")
async def get_model_metadata(model_name: str, model_version: str):
    interpreter = model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    return {
        'inputs_shape': input_details[0]['shape'].tolist()
    }


@app.post('/v1/models/{model_name}/versions/{model_version}:predict')
async def predict(model_name: str, model_version: str, payload: JSONStructure):
    interpreter = model_interpreters[model_name]
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_dtype = input_details[0]["dtype"]
    logging.info(
        f'interpreting with {model_name} for input type {input_dtype}')
    logging.warning(f'output details: {output_details}')

    try:
        input_data = payload[b'inputs']
        input_array = np.array(input_data, dtype=input_dtype)

        interpreter.set_tensor(input_details[0]["index"], input_array)

        interpreter.invoke()
        # Process image and get predictions
        prediction = {}

        if len(output_details) >= 3:
            boxes = interpreter.get_tensor(output_details[0]["index"])
            classes = interpreter.get_tensor(
                output_details[1]["index"]).astype(int) + 1
            scores = interpreter.get_tensor(output_details[2]["index"])

            logging.warning(
                f'interpreting with {model_name} for input type {input_dtype}')
            logging.warning(f'Boxes of object detected: {boxes[0]}')
            logging.warning(f'Classes of object detected: {classes[0]}')
            logging.warning(f'Scores of object detected: {scores[0]}')

            prediction = {
                'outputs': {
                    'detection_boxes': boxes.tolist(),
                    'detection_classes': classes.tolist(),
                    'detection_scores': scores.tolist()
                }
            }
        elif len(output_details) == 1:
            scores = interpreter.get_tensor(output_details[0]["index"])
            logging.warning(
                f'interpreting with {model_name} for input type {input_dtype}')
            logging.warning(f'Scores of classification: {scores[0]}')
            prediction = {'outputs': scores.tolist()}

        return prediction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
