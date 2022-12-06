# VIO-EDGE

Répertoire principal du code de Visual Inspection Orchestrator, une application permettant de vérifier la qualité de produits assemblés sur une chaîne de production industrielle.

## Documentation

https://octo-technology.github.io/VIO/



## Lancer la stack complète avec le Makefile

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


## Lancer la stack complète avec des commandes docker-compose

Un autre moyen de lancer toute la stack en une commande est le suivant :

```shell
$ docker-compose up -d --build
```

Celle-ci lance tous les services de la stack définis dans le [docker-compose.yml](docker-compose.yml). On peut ensuite les arrêter tous avec la commande (les containers seront arrêtés et supprimés) :

```shell
$ docker-compose down
```
