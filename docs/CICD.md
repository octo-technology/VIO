# La CICD

Nous utilisons la CI Gitlab pour l'intégration continue et pour le déploiement continu. Celle-ci est implémentée dans le fichiers [.gitlab-ci.yml](.gitlab-ci.yml).

La CI est composée de 3 étapes principales (stages) :

- Lint : analyse statique du code Python avec flake8
- Test : lancement des tests automatisés (tests unitaires, d'intégration, fonctionnels suivis du calcul de la pyramide des tests)
- Build : construction d'image Docker pour chaque application


Chaque étape de CI va être déclenchée sous l'une des deux conditions suivantes :

- si un nouveau commit est pushé sur master
- si une merge request est ouverte sur Gitlab

Pour déployer une nouvelle version sur RaspberryPI, il faut d'abord créer des images Docker spécifiques pour le device en question. 
Afin de créer ces images, il suffit d'ajouter un tag Git, en suivant la convention [SemVer](https://semver.org/lang/fr/). Par exemple:

```
git tag rpi-1.2.1
git push --tags
```

Une fois le tag poussé, cela déclenche une pipeline Gitlab CI qui va construire les images Docker pour RaspberryPI.
Celles-ci seront stockées dans la registry Gitlab, et elles-mêmes taguées avec le même tag `rpi-1.2.1`.

Enfin, il faut préciser à Azure IoT Hub qu'on souhaite déployer ces nouvelles versions sur les dispositifs Edge. 
Pour cela, il suffit mettre à jour les variables dans le fichier `deployment/ansible/setup_iot_hub_azure.yml` et relancer le playbook Ansible.

