# tensorflow-lite-rest-server
Expose tensorflow-lite models via a rest API. Currently object, face & scene detection is supported. Can be hosted on any of the common platforms including RPi, linux desktop, Mac and Windows. A service can be used to have the server run automatically on an RPi.

## Setup
In this process we create a virtual environment (venv), then install tensorflow-lite [as per these instructions](https://www.tensorflow.org/lite/guide/python) which is platform specific, and finally install the remaining requirements. **Note** on an RPi (only) it is necessary to system wide install pip3, numpy, pillow.

All instructions for mac using venv :
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Or using the makefiles to set up a conda env :

```
cd edge_model_serving/tflite_serving

make tflite_serving
conda activate tflite_serving
make install
```

## Models
For convenience a couple of models are included in this repo and used by default. A description of each model is included in its directory. Additional models are available [here](https://github.com/google-coral/edgetpu/tree/master/test_data).

If you want to create custom models, there is the easy way, and the longer but more flexible way. The easy way is to use [teachablemachine](https://teachablemachine.withgoogle.com/train/image), which I have done in this repo for the dogs-vs-cats model. The teachablemachine service is limited to image classification but is very straightforward to use. The longer way allows you to use any neural network architecture to produce a tensorflow model, which you then convert to am optimized tflite model. An example of this approach is described in [this article](https://towardsdatascience.com/inferences-from-a-tf-lite-model-transfer-learning-on-a-pre-trained-model-e16e7c5f0ee6), or jump straight [to the code](https://github.com/arshren/TFLite/blob/master/Transfer%20Learning%20with%20TFLite-Copy1.ipynb).

To convert models from model_serving, tensorflow .pb format to tflite fomat:

    python -m tflite_serving.convert_pb_to_tflite

## Run and Usage
Start the tflite-server on port 8501 :
```
(venv) $ uvicorn tflite_serving.tflite_server:app --reload --port 8501 --host 0.0.0.0
```

Or via Docker:

```
# Build for raspberry 
docker build --file tflite_serving/Dockerfile.raspberrypi --tag ghcr.io/octo-technology/vio/edge_tflite_serving.raspberrypi:latest .
# Run
docker run -p 8501:8501 ghcr.io/octo-technology/vio/edge_tflite_serving.raspberrypi:latest 
```
```
# Build for mac
docker build --file tflite_serving/Dockerfile --tag ghcr.io/octo-technology/vio/edge_tflite_serving:latest .
# Run for mac
docker run -p 8501:8501 ghcr.io/octo-technology/vio/edge_tflite_serving:latest
```

You can check that the tflite-server is running by visiting `http://ip:5000/` from any machine, where `ip` is the ip address of the host (`localhost` if querying from the same machine). The docs can be viewed at `http://localhost:5000/docs`

You can test the serving app with the live_test.py script
```
python -m tflite_serving.live_test
```


## Routes description

Swagger
    
[http://<IP>:8501/docs](http://<IP>:8501/docs)

Exposed models

[http://<IP>:8501/models](http://<IP>:8501/models)

Get image resolution expected by a specific model_name, model_version

[http://<IP>:8501/v1/models/{model_name}/versions/{model_version}/resolution](http://<IP>:8501/v1/models/{model_name}/versions/{model_version}/resolution)
    
Predict with a specific model_name, model_version

[http://<IP>:8501/v1/models/{model_name}/versions/{model_version}:predict](http://<IP>:8501/v1/models/{model_name}/versions/{model_version}:predict)



# Source: [https://github.com/robmarkcole/tensorflow-lite-rest-server](https://github.com/robmarkcole/tensorflow-lite-rest-server)
