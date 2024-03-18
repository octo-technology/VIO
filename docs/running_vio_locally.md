# Running VIO locally

In order to use VIO locally we are going to start 3 modules that will need conda installed.
The most direct way to install conda on MacOS is via Homebrew:
```
brew update
brew install --cask miniconda
```

## Running the edge model serving
The edge model serving is the module that is going to do the inference computing using the stored models. It is called
by the edge orchestrator.

You can follow the conda environment installation from the 
[edge model serving's ReadMe](../edge_model_serving/tflite_serving/README.md) file. Once it is done you can start the 
server using the make command.

```
make run_tflite_serving
```

## Running the edge orchestrator
The edge orchestrator will administrate the configuration, images captures, storage and communication with the edge
models for inference then applying business rules.
The following commands will create a package of the orchestrator environment as [described here](edge_orchestrator.md)
```
cd edge_orchestrator
make conda_env
make install
pip install -e .[dev]
```

It may be required for you to change the default profile of VIO depending on your needs. 

In the `VIO/edge_orchestrator/
edge_orchestrator/environment/default.py` file, you can connect the orchestrator to your edge serving API by giving its
adress to `SERVING_MODEL_URL`.
```
import os

class Default(Config):
    SERVING_MODEL_URL = os.environ.get(
        "SERVING_MODEL_URL", "http://0.0.0.0:8501"
    )
```

The default value of the Serving Wrapper is a `FakeModelForward`, which you can replace with a `TFServingWrapper` that you
imported.
```
from edge_orchestrator.infrastructure.model_forward.tf_serving_wrapper import (
    TFServingWrapper)

class Default(Config):
    def __init__(self):
        self.model_forward = TFServingWrapper(
            self.SERVING_MODEL_URL, self.inventory, self.station_config
        )
```

Now start the server :

```
python -m edge_orchestrator
```

## Running the interface
The interface is connected to the edge model serving, facilitating its usage.

You can follow the Edge Interface's [ReadMe file](../edge_interface/README.md) commands to run this part.

