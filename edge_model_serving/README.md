# Model Forward / Serving Instance

## Pull the tensorflow serving docker image

    docker pull tensorflow/serving

## Run the tensorflow-serving docker with the following command:

Define env variables

    MODELNAME="yolo3_harnais"

    MODELPATH="$(pwd)/modelforward/$MODELNAME"
    
Execute the docker run cmd from the repo roots

    docker run -p 8501:8501 -v "$MODELPATH:/models/$MODELNAME" -e MODEL_NAME=$MODELNAME -t tensorflow/serving
