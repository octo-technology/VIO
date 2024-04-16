# Running VIO locally

In order to use VIO locally we are going to start 3 modules in 3 different terminals. Some of them will need conda installed.
The most direct way to install conda on MacOS is via Homebrew:
```
brew update
brew install --cask miniconda
```

## Running the edge model serving
The edge model serving is the module that is going to do the inference computing using the stored models (_it does the_ `.predict()`"). It is called
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

It is now required to edit the configured environment according to a local run.
In the `VIO/edge_orchestrator/edge_orchestrator/api_config.py` file, inform the local profile on line 7.

```
def load_config():
    configuration = os.environ.get("API_CONFIG", "local")
```

Now start the server :

```
python -m edge_orchestrator
```

## Running the interface
The interface is connected to the edge model serving, facilitating its usage.

You can follow the Edge Interface's [ReadMe file](../edge_interface/README.md) commands to run this part.

