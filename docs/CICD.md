# La CICD

Nous utilisons les workflows de Github Actions pour l'intégration continue et pour le déploiement continu.

Il existe 5 workflows :

2 workflows de CI:

- [ci_edge_interface.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/ci_edge_interface.yml) :
  intégration continue de l'application
  edge_interface décomposée en 2 jobs
    - job `lint_and_test_on_edge_interface` : analyse statique du code JavaScript (pas de tests pour le moment)
    - job `build_and_push_images` : construction de l'image Docker de l'application sans publication dans une registry
- [ci_edge_orchestrator.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/ci_edge_orchestrator.yml) :
  intégration continue de l'application
  edge_orchestrator décomposée en 2 jobs
    - job `lint_and_test_on_edge_orchestrator` : analyse statique du code Python avec Flake8 suivie de l'exécution des
      tests automatisés (unitaires, intégration et fonctionnels) avec le stockage des rapports de tests dans Github
    - job `build_and_push_images` : construction de l'image Docker de l'application sans publication dans une registry

Les deux workflows de CI (edge_[interface|orchestrator]_ci.yml) sont déclenchés sous l'une des conditions suivantes :

- si une merge request comportant des différences est ouverte sur Github
- si un commit sur la branche master est pushé sur Github

3 worklows de release:

- [publication_vio_images.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_vio_images.yml) :
  publication des images Docker edge_serving par déclenchement manuel
    - job `build_and_push_images` : construction des images Docker avec publication des images dans la registry Github
- [publication_vio_images_raspberry.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_vio_images_raspberry.yml) :
  publication des images Docker edge_serving par déclenchement manuel
    - job `build_and_push_images` : construction des images Docker spécifique au hardware Raspberry avec publication des images dans la registry Github
- [publication_pages_gh-pages_branch.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_pages_gh-pages_branch.yml) :
  génération et déploiment de la documentation

Les 3 workflows de release sont déclenchés sous l'une des conditions suivantes :

- si une release est crée depuis Github


////////////////////////////// WIP //////////////////////////////

Pour déployer une nouvelle version sur RaspberryPI, il faut d'abord créer des images Docker spécifiques pour le device
en question.
Afin de créer ces images, il suffit d'ajouter un tag Git, en suivant la
convention [SemVer](https://semver.org/lang/fr/). Par exemple:

```
git tag rpi-1.2.1
git push --tags
```

Une fois le tag poussé, cela déclenche une pipeline Gitlab CI qui va construire les images Docker pour RaspberryPI.
Celles-ci seront stockées dans la registry Gitlab, et elles-mêmes taguées avec le même tag `rpi-1.2.1`.

Enfin, il faut préciser à Azure IoT Hub qu'on souhaite déployer ces nouvelles versions sur les dispositifs Edge.
Pour cela, il suffit mettre à jour les variables dans le fichier `deployment/ansible/setup_iot_hub_azure.yml` et
relancer le playbook Ansible.

////////////////////////////// WIP //////////////////////////////
