FROM tensorflow/serving:latest

# Do not copy the models.config file in the /models dir (mounted dir by docker-compose > will delete it!)
COPY tf_serving/models.config /home/

EXPOSE 8501
ENTRYPOINT ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_config_file=/home/models.config"]
