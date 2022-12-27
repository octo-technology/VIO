# Visual Inspection Orchestrator

![CI edge_orchestrator](https://github.com/octo-technology/VIO/actions/workflows/ci_edge_orchestrator.yml/badge.svg)
![CI edge_interface](https://github.com/octo-technology/VIO/actions/workflows/ci_edge_interface.yml/badge.svg)
![GitHub issues](https://img.shields.io/github/issues/octo-technology/VIO)

Visual Inspection Orchestrator is a modular framework made to ease the deployment of VI usecases.

*Usecase example: Quality check of a product manufactured on an assembly line.*

VIO full documentation can be found [here](https://octo-technology.github.io/VIO/)


The VIO modules are split between:

** Edge modules **: The VIO edge modules are deployed close to the object to inspect

- [The edge orchestrator](docs/edge_orchestrator.md)
- [The edge interface](docs/edge_interface.md)
- [The edge model serving](docs/edge_model_serving.md)
- [The edge deployment playbook](docs/edge_deployment.md)

** Hub modules **: The VIO hub modules are deployed in the cloud to collect data and orchestrate the edge fleet

- [The hub monitoring](docs/hub_monitoring.md)
- [The hub deployment playbook](docs/hub_deployment.md)


## Install the framework

`git clone git@github.com:octo-technology/VIO.git`

Prerequisites: 
- need docker installed
- need make installed

## Run the stack

To launch the stack you can use the [Makefile](../Makefile) on the root of the repository which define the different target based on the [docker-compose.yml](../docker-compose.yml):

- run all edge services (orchestrator, model-serving, interface, db) with local hub monitoring (grafana): `make vio-edge-up`

- stop and delete all running services : `make vio-edge-down`

To check all services are up and running you can run the command `docker ps`, you should see something like below:

 ![stack-up-with-docker](docs/images/stack-up-with-docker.png)

Once all services are up and running you can access:

- the swagger of the edge orchestrator API (OrchestratoAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- the swagger of the edge model serving: [http://localhost:8501/docs](http://localhost:8501/docs)
- the hub monitoring: [http://localhost:4000/login](http://localhost:4000/login)
- the edge interface: [http://localhost:8080](http://localhost:8080)

From the edge interface you can load a configuration and run the trigger button that will trigger the Core API and launch the following actions:

 ![vio-architecture-stack](docs/images/supervisor-actions.png)

# Releases

Build Type                    | Status                                                                                                                                                                           | Artifacts
----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------
**Docker images** | [![Status](https://github.com/octo-technology/VIO/actions/workflows/publication_vio_images.yml/badge.svg)](https://github.com/octo-technology/VIO/actions/workflows/publication_vio_images.yml/badge.svg) | [Github registry](https://github.com/orgs/octo-technology/packages)

## License

VIO is licensed under [Apache 2.0 License](docs/LICENSE.md)

## Contributing

Learn more about how to get involved on [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide
