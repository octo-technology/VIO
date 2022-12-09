### MLOPS framework

VIO framework propose a generic code base for each of the following MLOPS features:

- The data gathering
- The model monitoring
- The model factory
- The fleet management
- The software factory

 ![vio-mlops](images/vio_mlops.png)
 
### Modular framework

VIO core has been built following the hexagonal architecture patterns, therefore it can be adapted to its production environement constraints (cloud provider, hardware, ML framework...).

![vio-hexagonal-architecture](images/vio_hexagonal_architecture.png)

### Micro-services approach

Each sub folders below are indeed a module, an application, an independant micro service. Anyone of them is therefore functional by itself.
Les sous-dossiers du dossier courant, à savoir :

- [The core](supervisor.md) 
- [The deployment tools](deployment.md)
- [The fleet monitoring](monitoring.md)
- [The edge interface](edge_interface.md)
- [The model serving](model_serving.md)

All of those modules have been packages inside a dedicated docker images to facilitate their deployment.
