FROM tensorflow/serving:latest

WORKDIR /models
COPY ../models/tf ./models
COPY ./models.config ./models/models.config

RUN echo '#!/bin/bash \n\n\
tensorflow_model_server --port=8500 --rest_api_port=8501 \
--model_config_file=/models/models.config' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
