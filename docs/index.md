# VIO-EDGE

Répertoire principal du code de Visual Inspection Orchestrator, une application permettant de vérifier la qualité de produits assemblés sur une chaîne de production industrielle.

## Table des matières
[[_TOC_]]


## Utilisation

Pour pouvoir lancer la stack complète, la dépendance minimale et suffisante est docker.
Voilà un aperçu de la stack : ![supervisor-architecture-stack](supervisor-architecture-stack.png)


### Lancer la stack complète avec le Makefile

Pour lancer l'ensemble de la stack, le [Makefile](Makefile) définit des targets, s'appuyant sur le [docker-compose.yml](docker-compose.yml), permettant de :

- lancer tous les services (supervisor, model-serving, Mongo DB, UI) : `make services-up`
- lancer le supervisor conteneurisé : `make supervisor`
- lancer le model-serving conteneurisé : `make model_serving`
- lancer l'ui conteneurisé : `make ui`
- arrêter et supprimer tous les services : `make services-down`

Chacune des targets précédentes correspond à une commande [docker-compose.yml](docker-compose.yml).

Par exemple, la target `supervisor` correspond à :

```shell
$ docker-compose up -d --build supervisor
```


### Lancer la stack complète avec des commandes docker-compose

Un autre moyen de lancer toute la stack en une commande est le suivant :

```shell
$ docker-compose up -d --build
```

Celle-ci lance tous les services de la stack définis dans le [docker-compose.yml](docker-compose.yml). On peut ensuite les arrêter tous avec la commande (les containers seront arrêtés et supprimés) :

```shell
$ docker-compose down
```


## L'approche micro-service

Les sous-dossiers du dossier courant, à savoir :

- model_serving
- supervisor
- ui

sont chacun un module, une application, un micro-service indépendant. Chacun d'eux est donc fonctionnel seul (modulo une BD pour supervisor).

Ces micro-services (ou modules ou applications) sont tous (ou presque) packagés sous forme d'image Docker pour faciliter leur déploiement.


## Développement
Cf [README.md](./supervisor/README.md).


## La CI Gitlab et le déploiement

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


# Grafana
cf [README](./monitoring/README.md)

Prerequisites for the cmd 
```
make deploy-grafana-azure:
```
install sshpass,
    - on mac: 
    ```
    brew install hudochenkov/sshpass/sshpass
    ```
    - on linux
    ```
    apt-get install sshpass
    ```

