FROM --platform=$TARGETPLATFORM tensorflow/serving:latest
FROM --platform=$TARGETPLATFORM emacski/tensorflow-serving

WORKDIR /models

COPY models/tf/ /models/tf/
COPY tf_serving/models.config /models/models.config

EXPOSE 8501
ENTRYPOINT ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_config_file=/models/models.config"]
