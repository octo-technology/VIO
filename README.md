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
- run the core (supervisor) containerized : `make supervisor`
- run the model serving containerized: `make model_serving`
- run the edge interface containerized : `make ui`
- stop and delete all running services : `make services-down`


## License

VIO is licensed under [Apache 2.0 License](docs/LICENSE.md)

## Contributing

Learn more about how to get involved on [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide
