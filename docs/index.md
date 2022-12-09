# Getting Started

Visual Inspection Orchestrator is a modular framework made to ease the deployment of VI usecases.

Usecase example: Quality check of a product manufactured on an assembly line.


## Features

- [The core](docs/supervisor.md) 
- [The deployment tools](docs/deployment.md)
- [The fleet monitoring](docs/monitoring.md)
- [The edge interface](docs/edge_interface.md)
- [The model serving](docs/model_serving.md)


## Install the framework

To launch the complete stack, you'll need a minima docker install on your machine.

`git clone git@github.com:octo-technology/VIO.git`

## Run the stack

To launch the stack you can use the [Makefile](../Makefile) on the root of the repository which define the different target based on the [docker-compose.yml](../docker-compose.yml):

- run all services (supervisor, model-serving, Mongo DB, UI) : `make services-up`
- run the core (supervisor) containerized : `make supervisor`
- run the model serving containerized: `make model_serving`
- run the edge interface containerized : `make ui`
- stop and delete all running services : `make services-down`

Each of the above target correspond to a command [docker-compose.yml](../docker-compose.yml). For example, the target `supervisor` correspond to :

```shell
$ docker-compose up -d --build supervisor
```

To check all services are up and running you can run the command `docker ps`, you should see something like below:

CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS          PORTS                      NAMES
f904fccdcc86   vio_edge_interface       "/docker-entrypoint.…"   10 minutes ago   Up 10 minutes   0.0.0.0:8080->80/tcp       edge_interface
133afdb77dc3   vio_supervisor           "/bin/sh -c 'python …"   25 minutes ago   Up 25 minutes   0.0.0.0:8000->8000/tcp     supervisor
58dfa3a848a3   grafana/grafana:latest   "/run.sh"                33 minutes ago   Up 33 minutes   0.0.0.0:4000->3000/tcp     grafana
cc41c331d6a8   mongo:5.0.2              "docker-entrypoint.s…"   33 minutes ago   Up 33 minutes   0.0.0.0:27017->27017/tcp   mongodb
ce1b26e7c794   vio_model_serving        "uvicorn tflite_serv…"   33 minutes ago   Up 33 minutes   0.0.0.0:8501->8501/tcp     model_serving


Once all services are up and running you can access:

- the swagger of the core API (OrchestratoAPI): http://localhost:8000/docs
- the swagger of the model serving: http://localhost:8501/docs
- the monitoring grafana: http://localhost:4000/login
- the edge interface: http://localhost:8080

From the edge interface you can load a configuration and run the trigger button that will trigger the Core API and launch the following actions:

 ![vio-architecture-stack](images/supervisor-actions.png)

## Implementation example

Here you can find an implementation of VIO deployed on Azure managing a fleet of Raspberrys:
 
 ![vio-architecture-stack](images/vio_azure_stack.png)
