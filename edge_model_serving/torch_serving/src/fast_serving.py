import logging
import os
from pathlib import Path
from typing import Any, AnyStr, Dict, Union, List
from fastapi import FastAPI, HTTPException
import numpy as np

from modelhandler import ModelHandler

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

app = FastAPI()

coral_tpu = os.environ.get('TPU', 'false')


def create_interpreter(model_directory: Path):
    logging.info(f'Loading model: {model_directory}')
    model_handler = ModelHandler(checkpoint_pth=model_directory)
    model_handler.load_model(cpu=True)
    return model_handler

# Create the different interpreters
model_interpreters = {}

weight_path = Path.cwd().parent.parent / "models" / "checkpoint_ssd300.pth.tar"
model_interpreters["ols-smart-rack"] = create_interpreter(model_directory=weight_path)


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
    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()

    # input_dtype = input_details[0]["dtype"]
    # logging.info(f'interpreting with {model_name} for input type {input_dtype}')
    # logging.warning(f'output details: {output_details}')

    try:
        input_data = payload[b'inputs']
        
        input_array = np.array(input_data, dtype=np.uint8)

        # interpreter.set_tensor(input_details[0]["index"], input_array)

        boxes, classes, scores = interpreter.handle(data=input_array)

        # logging.warning(f'interpreting with {model_name} for input type {input_dtype}')
        logging.info(f'Boxes of object detected: {boxes}')
        logging.info(f'Classes of object detected: {classes}')
        logging.info(f'Scores of object detected: {scores}')

        prediction = {
            'outputs': {
                'detection_boxes': [boxes],
                'detection_classes': [classes],
                'detection_scores': [scores]
            }
        }

        return prediction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
