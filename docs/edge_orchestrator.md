# Edge Orchestrator

The edge_orchestrator orchestrates the following steps as soon as it is triggered:

1. image capture
2. image backup
3. metadata backup
4. model inference on images
5. saving results

 ![vio-architecture-stack](images/edge_orchestrator-actions.png)

## Set up your development environment

To facilitate the installation of the development environment, a [Makefile](https://github.com/octo-technology/VIO/blob/main/edge_orchestrator/Makefile)  automates tasks:

    $ make
    ❓ Use `make <target>'
    conda_env                       🐍 Create a Python conda environment
    dependencies                    ⏬ Install development dependencies
    tests                           ✅ Launch all the tests
    unit_tests                      ✅ Launch the unit tests
    integration_tests               ✅ Launch the integration tests
    functional_tests                ✅ Launch the functional tests
    pyramid                         ⨺ Compute the tests pyramid
    pyramid_and_badges              📛 Generate Gitlab badges

** Python interpreter installation **

The project uses `conda` to manage Python virtual environments [Miniconda installation guide](https://docs.conda.io/en/latest/miniconda.html).

** Install conda on MacOS **

The most direct way to install `conda` is still Homebrew:

    brew update
    brew install --cask miniconda

** Initialize the project environment **

Once Miniconda is installed, create the Python virtual environment and install its dependencies using the Makefile:

    cd edge_orchestrator
    make conda_env

** Install project dependencies **

    make dependencies

** Setuptools "editable mode" **

To be able to benefit from Python packaging without being impacted during local development (i.e. without having to rebuild a package each time it is updated), we use the editable mode (see the official pip [doc](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable)).

    pip install -e .

During the installation of the development environment, the above command will have the following effect:

A file edge_orchestrator.egg-link was created in the edge_orchestrator virtual environment with the following content:

    cat /usr/local/Caskroom/miniconda/base/envs/edge_orchestrator/lib/python3.9/site-packages/edge_orchestrator.egg-link
    /path/to/project/sources/vio_edge/edge_orchestrator

Thus, thanks to the egg-link, the python module edge_orchestrator is properly installed as a library in the virtual environment, but does not require regular repackaging after an update in local.

** Setuptools "development mode" **

To be able to install the library and its development dependencies (test libraries):

    pip install -e ".[dev]"

** Setuptools "console_scripts" EntryPoints **

In the [edge_orchestrator.egg-link](/usr/local/Caskroom/miniconda/base/envs/edge_orchestrator/lib/python3.9/site-packages/edge_orchestrator.egg-link) file of the edge_orchestrator, the following entry_points block is configured

```python
setup(
    name="edge_orchestrator",
    # [...]
   entry_points={
      'console_scripts': [
         'edge_orchestrator = edge_orchestrator.__main__:main',
      ],
   },
)
```

The `setuptools` package allows you to configure different types of scripts, including console_scripts, which will generate a "shim" shell script that will be placed on the PATH and will call the edge_orchestrator.__main__:main function as configured.

This edge_orchestrator [edge_orchestrator](/usr/local/Caskroom/miniconda/base/envs/edge_orchestrator/bin/edge_orchestrator)  is located in the virtual environment created during project installation.

When the virtual environment is activated (by running `conda` activate edge_orchestrator), the $PATH environment variable is configured to point to the bin/ folder of the virtual environment.

```shell
$ echo $PATH
/usr/local/Caskroom/miniconda/base/envs/edge_orchestrator/bin:[...]
```

If we look inside this script, we notice that it is responsible for importing our edge_orchestrator module and calling its entry point.

```shell
#!/usr/local/Caskroom/miniconda/base/envs/edge_orchestrator/bin/python3.9
# EASY-INSTALL-ENTRY-SCRIPT: 'edge_orchestrator','console_scripts','edge_orchestrator'
import re
import sys

# for compatibility with easy_install; see #2198
__requires__ = 'edge_orchestrator'

from pkg_resources import load_entry_point

[...]

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(load_entry_point('edge_orchestrator', 'console_scripts', 'edge_orchestrator')())
```
For more information, the documentation can be found [here](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html).

## Tests

To run all tests:

    make tests

To run only unit tests:

    make unit_tests

## API Routes

All routes are prefixed with api/v1. For example, to retrieve the list of items locally, use this url: 
[http://localhost:8000/api/v1/items](http://localhost:8000/api/v1/items)

You can also refer to the API swagger on the /docs url: [http://localhost:8000/docs](http://localhost:8000/docs)

## Add a new configuration 

All the JSON config files are in `edge_orchestrator/config/station_configs`
If you want to create a new config, you need to add a new JSON in the above directory.
Here's a template of a config file.

```
{
  "cameras": {
    "camera_id3": {
      "type": "fake" #type of the camera : fake, pi_camera or usb_camera
      "input_images_folder": "people_dataset",
      "position": "front",
      "exposition": 100,
      "models_graph": {
        "model_id1": {
          "name": "mobilenet_ssd_v2_coco", #name of the model
          "depends_on": [], #if this model depends on another model, if none then empty list
          "class_to_detect": ["cell phone"] #class to detect, always in list format and only for object detection model. If classification model, can delete this row
        },
        "model_id6": {
          "metadata": "cellphone_connection_control",#name of the model
          "depends_on": [ 
            "model_id1"
          ], #the model_id6 depends on the model_id1
          "class_to_detect": ["connected"]
        }
      },
      "camera_rule": {
        "name": "min_nb_objects_rule", #name of the camera rule
        "parameters": {
          "class_to_detect": ["person"], #always a list
          "min_threshold": 1
        }
      }
    },
    "camera_id2": { # if there's another camera, if not you can delete this section, if there's a third then add one.
      "type": "fake",
      "input_images_folder": "people_dataset",
      "position": "front",
      "exposition": 100,
      "models_graph": {
        "model_id1": {
          "name": "mobilenet_ssd_v2_face",
          "depends_on": [],
          "class_to_detect": ["face"]
        }
      },
      "camera_rule": {
        "name": "min_nb_objects_rule",
        "parameters": {
          "class_to_detect": ["face"],
          "min_threshold": 1
        }
      }
    }
  },
  "item_rule": {
    "name": "min_threshold_KO_rule", #the item rule name
    "parameters": {
      "threshold": 1
    }
  }
}
```

The comments are only here to guide you, you should delete them in your new json config.

 Station config : Camera        | Description                                                                             
-----------------|-----------------------------------------------------------------------
 `type` | Camera type can be `fake`, `pi_camera` and `usb_camera`. `pi_camera` will be used for raspberry deployment. `usb_camera` is used when it is required to find a camera or webcam connected to the edge. A `fake` camera will not capture image but pick a random .jpg or .png file in the folder pointed by the "input_images_folder" parameter, which will be located in edge_orchestrator/data/<input_images_folder>.
 `input_images_folder` | Used with `fake` cameras, is the path to the folder from which the pictures are taken.
 `position` | Used for metadata, purpose of saving the camera parameters in the future
 `exposition` | Used for metadata, purpose of saving the camera parameters in the future
 `models_graph` | Pipeline of models used during inference. Dictionary of models, containing their names, depencecies to other models and all its possible parameters.
 `camera_rule` | Dictionary, key `name` containing the rule name and key `parameters` containing the selected rule's inputs 

For the item rules, just inform the rule's `name` and `parameters` as a dictionary of the inputs.




## Add a new model

- All our models are in tflite format. In order to add an already trained model in the ```flite_serving ``` folder. 
Inside this folder should be the .tflite model and if needed a .txt file with the labels/class names.

- You also need to add this model in the inventory located in ````edge_orchestrator/config/inventory.json```` under the 
````models ```` category. 
  - Classification model
    ```
      "your_new_model_name": {
      "category": "classification",
      "version": 1,
      "class_names": [
        "class name 1",
        "class name 2",
         ...
      ],
      "image_resolution": [
        x resolution for your trained model (int),
        y resolution for your trained model (int)
      ]
    }
    ```
  - Object detection model
    ```
    "your_new_model_name": {
      "category": "object_detection",
      "version": 1,
      "class_names_path": "{name of file with the class names}.txt",
      "output": {
        "boxes_coordinates": "{name of the boxes_coordinates variable in your model}",
        "objectness_scores": "{name of the objectness_scores variable in your model}",
        "number_of_boxes": "{name of the number_of_boxes variable in your model}",
        "detection_classes": "{name of the detection_classes variable in your model}"
      },
      "image_resolution": [
        x resolution for your trained model (int),
        y resolution for your trained model (int)
      ],
      "objectness_threshold": minimum threshold score for an object to be detected (float)

    }
    ```

 Model parameters        | Description                                                                             
------------------------|---------------------------------------------------------------------------
 `category` | Model's category, can be `object_detection`, `classification` or `object_detection_with_classification`
 `version`  |  Model's version, used in the API link, should be 1 __mais c'est pas utilisé__
 `model_type`  |  Type of model used, is `Mobilenet` or `yolo`. Mobilenet models return boxes as [ymin, xmin, ymax, xmax] and Yolo as [x_center, y_center, width, height]
 `image_resolution` | List of ints corresponding to the x.y image size ingested by the model
 `depends_on` | Used to design model pipelines, is a list of models' names
 `class_names` | List of the label names as a list of strings 
 `class_names_path` | Path to the labels files, the file should be located under the `edge_orchestrator/data` folder
 `class_to_detect` | List of label names that will be detected (for Mobilenet)
 `output: detection_boxes` | For detection models, name which will be given to the predicted boxes
 `output: detection_scores` | For detection models, name which will be given to the predicted scores
 `output: detection_classes` | For detection models, name which will be given to the predicted classes
 `output: detection_metadata` | For detection models, name which will be given to the predicted metadata
 `objectness_threshold` | Score threshold under which an object won't be detected

## Add new camera rule
In order to make a final decision i.e the item rule, we first need camera rules. Each camera gets a rule.
- Each rule is in a distinct file located in  ``` edge_orchestrator/edge_orchestrator/domain/model/business_rules/camera_business_rules ```
It's in this method that's the camera rule will be described. 
The method only takes the inference in argument.

- You also need to precise the camera rule in the station config in ```edge_orchestrator/config/station_configs/```

```
"camera_rule": {
        "name": "name of the rule",
        "parameters": {
          # parameters of the rules for example : 
          "expected_label": ["connected"]
        }
      }

```

- You need to add the new rule in the ```get_camera_rule``` function located in ``` edge_orchestrator/edge_orchestrator/domain/model/camera.py ```
which get the good method from the name of the camera rule in the station config file. 

## Add new item rule

This is to make a final decision i.e the item rule. Each station config gets an item rule (only one).
- Each rule is in a distinct file located in  ``` edge_orchestrator/edge_orchestrator/domain/model/business_rules/item_business_rules ```
It's in this method that's the item rule will be described. 
The method only takes the camera decisions in argument.

- You also need to precise the item rule in the station config in ```edge_orchestrator/config/station_configs/```

```
  "item_rule": {
    "name": "name of the item rule",
    "parameters": {
    # parameters of the rules for example : 
      "threshold": 1
    }
  }

```

- You need to add the new rule in the ```get_item_rule``` function located in ``` edge_orchestrator/edge_orchestrator/domain/model/item.py ```
which get the good method from the name of the item rule in the station config file. 

The camera and item rules are called in the edge_orchestrator method ```edge_orchestrator/edge_orchestrator/domain/use_cases/edge_orchestrator.py``` 
in the ``` apply_business_rules ``` function.

## Adapters description

### Binary storage adapter

When an image is captured by any camera, VIO is saving the image in a storage. The binary storage adapter is responsible
this process. 4 binary storage systems are implemented in VIO:
- File System Binary Storage: Saves the image in the filesystem under the `VIO/edge_orchestrator/data/storage` folder.
- Memory Binary Storage: Saves the image in memory as a dictionary.
- Azure Container Binary Storage: Saves the images in an Azure Blob Storage container.
- GCP Binary Storage: Saves the images in a Google Cloud Storage bucket.

Theses adapters are implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/binary_storage` folder and 
the base mock class is defined `edge_orchestrator/edge_orchestrator/domain/ports/binary_storage.py`.

### Camera adapter

The camera adapter is responsible for localizing the connected cameras and capturing images, 3 camera systems are 
implemented in VIO and are chosen in the model configuration:
- Fake Camera: Picks a random .jpg or .png file in the folder pointed by the "input_images_folder" parameter, 
which will be located in edge_orchestrator/data/<input_images_folder>.
- Pi Camera: Used for Raspberry deployments to capture the images.
- USB Camera: Used when to find the connected cameras or webcams and capture images.

Theses adapters are implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/camera` folder and the base 
Camera class from which the adapters inherit is defined in `edge_orchestrator/edge_orchestrator/domain/models/camera.py`.

### Inventory adapter

Used to store the configuration settings. One adapter is available for json configuration files.
- Json Inventory: Reads the configuration from a json file.

This adapter is implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/inventory` folder and the base
mock Inventory class is defined in `edge_orchestrator/edge_orchestrator/domain/ports/inventory.py`.

### Metadata storage adapter

When a task is done, the configuration and the results are saved in a metadata storage. An example of the stored data
is shown below:

<details><summary><b>Metadata json</b></summary><p>

```
"serial_number": "serial_number",
    "category": "category",
    "station_config": "yolo_coco_nano_with_1_fake_camera",
    "cameras": {
      "camera_id4": {
        "brightness": null,
        "exposition": 100,
        "position": "back",
        "source": "people_dataset"
      }
    },
    "received_time": "2024-04-02 11:22:12",
    "inferences": {
      "camera_id4": {
        "model_id4": {
          "object_1": {
            "label": "person",
            "location": [
              0.2731,
              0.1679,
              0.5308,
              0.9438
            ],
            "score": 0.9098637104034424,
            "metadata": null
          },
          "object_2": {
            "label": "person",
            "location": [
              0.1099,
              0.351,
              0.2252,
              0.6945
            ],
            "score": 0.559946596622467,
            "metadata": null
          }
        }
      }
    },
    "decision": "OK",
    "state": "Done",
    "error": null,
    "id": "03a7adc7-59d5-4190-8160-4a71fd07cac5"
```
</p></details>

4 metadata storage systems are implemented in VIO:
- File System Metadata Storage: Saves the metadata in the filesystem under the `VIO/edge_orchestrator/edge_orchestrator/data/storage` folder.
- Memory Metadata Storage: Saves the metadata in memory as a dictionary.
- Azure Container Metadata Storage: Saves the metadata in an Azure Blob Storage container.
- GCP Metadata Storage: Saves the metadata in a Google Cloud Bucket.
- MongoDB Metadata Storage: Saves the metadata in a MongoDB database.

Theses adapters are implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/metadata_storage` folder and 
the base mock class is defined `edge_orchestrator/edge_orchestrator/domain/ports/metadata_storage.py`.

### Model forward adapter

The model forward adapter is responsible for the model inference, it performs the inference with the required post and 
pre-processing. 5 model forward systems are implemented in VIO:
- Fake Model Forward: Returns a random inference result.
- TF Serving Wrapper: Redirect the prediction task to one of the 3 following Tensor Flow model forwarders.
- TF Serving Detection Wrapper: Performs the inference with a detection model.
- TF Serving Classification Wrapper: Performs the inference with a classification model.
- TF Serving Detection and Classification Wrapper: Performs the inference with a detection and classification model.

Theses adapters are implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/model_forward` folder and
the base mock class is defined `edge_orchestrator/edge_orchestrator/domain/ports/model_forward.py`.

### Station config adapter

Used to store the station configuration settings. One adapter is available for json configuration files.

This adapter is implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/station_config` folder and the base
mock StationConfig class is defined in `edge_orchestrator/edge_orchestrator/domain/ports/station_config.py`.

### Telemetry sink adapter

Sends the telemetry data to a sink for further processing and analysis. 3 telemetry sink systems are implemented in VIO:
- Fake Telemetry Sink: Does nothing.
- Azure Telemetry Sink: Sends the telemetry data to an Azure IoT Hub Module.
- Postgresql Telemetry Sink: Sends the telemetry data to a Postgresql database.

Theses adapters are implemented in the `edge_orchestrator/edge_orchestrator/infrastructure/telemetry_sink` folder and
the base mock class is defined `edge_orchestrator/edge_orchestrator/domain/ports/telemetry_sink.py`.