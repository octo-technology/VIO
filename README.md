![edge_orchestrator CI](https://github.com/octo-technology/VIO/actions/workflows/edge_orchestrator_ci.yml/badge.svg)![GitHub issues](https://img.shields.io/github/issues/octo-technology/VIO)
# VIO-EDGE

Visual Inspection Orchestrator is a modular framework made to ease the deployment of VI usecases.

Usecase example: Quality check of a product manufactured on an assembly line.

VIO full documentation can be found [here](https://octo-technology.github.io/VIO/)

## Features

- [The core](docs/supervisor.md) 
- [The deployment tools](docs/deployment.md)
- [The fleet monitoring](docs/monitoring.md)
- [The edge interface](docs/edge_interface.md)
- [The model serving](docs/model_serving.md)

## Install the framework

`git clone git@github.com:octo-technology/VIO.git`

Prerequisites: 
- need docker installed
- need make installed

## Run the stack

To launch the stack you can use the [Makefile](../Makefile) on the root of the repository which define the different target based on the [docker-compose.yml](../docker-compose.yml):

- run all services (supervisor, model-serving, Mongo DB, UI) : `make services-up`

- stop and delete all running services : `make services-down`

To check all services are up and running you can run the command `docker ps`, you should see something like below:

 ![stack-up-with-docker](docs/images/stack-up-with-docker.png)

Once all services are up and running you can access:

- the swagger of the core API (OrchestratoAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- the swagger of the model serving: [http://localhost:8501/docs](http://localhost:8501/docs)
- the monitoring grafana: [http://localhost:4000/login](http://localhost:4000/login)
- the edge interface: [http://localhost:8080](http://localhost:8080)

From the edge interface you can load a configuration and run the trigger button that will trigger the Core API and launch the following actions:

 ![vio-architecture-stack](docs/images/supervisor-actions.png)

## License

VIO is licensed under [Apache 2.0 License](docs/LICENSE.md)

## Contributing

Learn more about how to get involved on [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide
