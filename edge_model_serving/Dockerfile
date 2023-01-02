FROM tensorflow/serving:latest

WORKDIR /models
COPY ./inception /models/inception
COPY ./mobilenet_v1_640x640 /models/mobilenet_v1_640x640
COPY ./mask_classification_model /models/mask_classification_model
COPY ./marker_quality_control /models/marker_quality_control
COPY ./models.config /models/models.config

RUN echo '#!/bin/bash \n\n\
tensorflow_model_server --port=8500 --rest_api_port=8501 \
--model_config_file=/models/models.config' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
