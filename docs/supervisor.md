# Le Core: Supervisor

Le supervisor orchestre les étapes suivantes dès qu'il est déclenché :

1. capture d'images
2. sauvegarde des images
3. sauvegarde des metadata
4. faire l'inférence des modèles sur les images
6. sauvegarde des résultats

## Développement

Pour faciliter l'installation de l'environnement de développment, un [Makefile](https://github.com/octo-technology/VIO/blob/main/supervisor/Makefile) automatise les tâches:
```shell
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
```


### Installation de l'interpréteur Python

Le projet utilise `conda` pour gérer les environnements virtuels Python [Guide d'installation Miniconda](https://docs.conda.io/en/latest/miniconda.html).

#### MacOS

La façon la plus directe pour installer `conda` reste Homebrew :
```shell
$ brew update
$ brew install --cask miniconda
```

#### Initialiser l'environnement projet

Une fois Miniconda installé, créer l'environnement virtuel Python et installer ses dépendences via le Makefile :
```shell
$ cd supervisor
$ make conda_env
```

#### Installation des dépendances projet
```shell
$ make dependencies
```

### Setuptools "editable mode"

Pour pouvoir bénéficier du packaging Python sans être impacté lors du développement en local (ie. sans devoir reconstruire un package à chaque modification), nous utilisons le mode `editable` (cf la [doc](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable) officielle de pip).

```shell
$ pip install -e .
```

Lors de l'installation de l'environnement de développement la commande ci-dessus va produire l'effet suivant:
- Un fichier [supervisor.egg-link](/usr/local/Caskroom/miniconda/base/envs/supervisor/lib/python3.9/site-packages/supervisor.egg-link) a été créé dans l'environnement virtuel supervisor avec le contenu suivante :

```shell
$ cat /usr/local/Caskroom/miniconda/base/envs/supervisor/lib/python3.9/site-packages/supervisor.egg-link
/path/to/project/sources/vio_edge/supervisor
```

Ainsi grâce au `egg-link`, le module python `supervisor` est bien installé comme librairie dans l'environnement virtuel, mais permet de ne pas avoir à repackager régulièrement après une mise à jour en local.

### Setuptools "development mode"

Pour pouvoir installer la librairie et ses dépendences de développement (librairies de tests):
```shell
$ pip install -e ".[dev]"
```

### Setuptools "console_scripts" EntryPoints

Dans le fichier [setup.py](https://github.com/octo-technology/VIO/blob/main/supervisor/setup.py) du supervisor, le bloc `entry_points` suivant est configuré :

```python
setup(
    name="supervisor",
    # [...]
   entry_points={
      'console_scripts': [
         'supervisor = supervisor.__main__:main',
      ],
   },
)
```

L'outil de packaging `setuptools` permet de configurer différents types de scripts, notamment les `console_scripts` qui vont permettre la génération d'un script shell "shim", qui sera positionné sur le PATH, et se chargera d'appeler la fonction `supervisor.__main__:main` tel que configuré

Ce script [supervisor](/usr/local/Caskroom/miniconda/base/envs/supervisor/bin/supervisor) se situe dans l'environnement virtuel créé lors de l'installation du projet.

Lorsque l'on active l'environnement virtuel (en faisant `conda activate supervisor`), la variable d'environnement `$PATH` est configurée pour pointer vers le dossier `bin/` de l'environnement virtuel.

```shell
$ echo $PATH
/usr/local/Caskroom/miniconda/base/envs/supervisor/bin:[...]
```

Si on regarde à l'intérieur de ce script, on remarque qu'il se charge d'importer notre module `supervisor` et d'en appeler l'entry point.

```shell
#!/usr/local/Caskroom/miniconda/base/envs/supervisor/bin/python3.9
# EASY-INSTALL-ENTRY-SCRIPT: 'supervisor','console_scripts','supervisor'
import re
import sys

# for compatibility with easy_install; see #2198
__requires__ = 'supervisor'

from pkg_resources import load_entry_point

[...]

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(load_entry_point('supervisor', 'console_scripts', 'supervisor')())
```

Pour plus d'information, la documentation se trouve [ici](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html).

## Tests
Pour exécuter tous les tests:
```shell
$ make tests
```

Pour exécuter seulement les tests unitaires:
```shell
$ make unit_tests
```

## Routes API

Toutes les routes sont préfixées par `api/v1`. Par exemple pour récupérer la liste des items en local, il faut utiliser cette url: `http://localhost:8000/api/v1/items`

## Add a new configuration 

All the JSON config files are in `supervisor/config/station_configs`
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
          "metadata": "mobilenet_ssd_v2_coco", #name of the model
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
          "metadata": "mobilenet_ssd_v2_face",
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

## Add a new model

- All our models are in tflite format. In order to add an already trained model in the ```flite_serving ``` folder. 
Inside this folder should be the .tflite model and if needed a .txt file with the labels/class names.

- You also need to add this model in the inventory located in ````supervisor/config/inventory.json```` under the 
````models ```` category. 
  - Classification model
    ```
      "your_new_model_name": {
      "category": "classification",
      "version": 1,
      "pb_file_path": "modelforward/your_new_model_name",
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
      "pb_file_path": "modelforward/your_new_model_name",
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


## Add new camera rule
In order to make a final decision i.e the item rule, we first need camera rules. Each camera gets a rule.
- Each rule is in a distinct file located in  ``` supervisor/supervisor/domain/model/business_rules/camera_business_rules ```
It's in this method that's the camera rule will be described. 
The method only takes the inference in argument.

- You also need to precise the camera rule in the station config in ```supervisor/config/station_configs/```

```
"camera_rule": {
        "name": "name of the rule",
        "parameters": {
          # parameters of the rules for example : 
          "expected_label": ["connected"]
        }
      }

```

- You need to add the new rule in the ```get_camera_rule``` function located in ``` supervisor/supervisor/domain/model/camera.py ```
which get the good method from the name of the camera rule in the station config file. 

## Add new item rule

This is to make a final decision i.e the item rule. Each station config gets an item rule (only one).
- Each rule is in a distinct file located in  ``` supervisor/supervisor/domain/model/business_rules/item_business_rules ```
It's in this method that's the item rule will be described. 
The method only takes the camera decisions in argument.

- You also need to precise the item rule in the station config in ```supervisor/config/station_configs/```

```
  "item_rule": {
    "name": "name of the item rule",
    "parameters": {
    # parameters of the rules for example : 
      "threshold": 1
    }
  }

```

- You need to add the new rule in the ```get_item_rule``` function located in ``` supervisor/supervisor/domain/model/item.py ```
which get the good method from the name of the item rule in the station config file. 

The camera and item rules are called in the supervisor method ```supervisor/supervisor/domain/use_cases/supervisor.py``` 
in the ``` apply_business_rules ``` function.
