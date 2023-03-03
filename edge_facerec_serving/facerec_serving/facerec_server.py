import logging
import os
from pathlib import Path
from typing import Any, AnyStr, Dict, Union, List
from fastapi import FastAPI, HTTPException
import numpy as np
import face_recognition

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

app = FastAPI()

coral_tpu = os.environ.get('TPU', 'false')


def load_allowed_faces():
    """
    Load allowed faces from the allowed_photos folder and convert them to features.
    """
    ref_imgs = []
    for file in os.listdir("allowed_photos"):
        if os.path.isfile(os.path.join("allowed_photos", file)):
            if file != ".DS_Store":
                ref = face_recognition.load_image_file(os.path.join("allowed_photos", file))
                ref_enc = face_recognition.face_encodings(ref)[0]
                ref_imgs.append(ref_enc)
    return ref_imgs


allowed_features = load_allowed_faces()

model_interpreters = {"face recognition model": None}


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
async def predict(payload: JSONStructure):
    try:
        input_data = payload[b'inputs']
        input_array = np.array(input_data[0])
        # reversing perform_pre_processing from tf_serving_classification_wrapper.py to fit facerec input format
        input_array = ((input_array + 1) * 127.0)
        input_array = input_array.astype("uint8")
        # Finding faces in uploaded image
        faces_ing_img = face_recognition.face_encodings(input_array)
        # if no faces found, return as VILAIN proba = 1 (KO)
        if len(faces_ing_img) == 0:
            return {'outputs': [[0, 1]]}
        # Get the encoding of the first face. Could be changed to check all faces on the image
        tocheck_enc = faces_ing_img[0]

        distances = []
        # Now we check if the query image contains a face found in allowed faces features loaded at the start of the
        # server by load_allowed_faces()
        for i_allowed in range(0, len(allowed_features)):
            ref_enc = allowed_features[i_allowed]
            # computing distance between the query and allowed faces.
            results = face_recognition.face_distance([tocheck_enc], ref_enc)
            # Distance is computed between 0 and 1. The smallest the best match
            distances.append(1 - results[0])

        # We compute the max "proba" to check if the query appears in allowed faces
        max_proba = np.array(distances).max()
        # we return probas as [ALLOWED,NOT ALLOWED]
        prediction = {'outputs': [[max_proba, 1 - max_proba]]}

        return prediction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
