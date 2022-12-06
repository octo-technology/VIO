# Visual Inspection Orchestrator

Répertoire principal du code de Visual Inspection Orchestrator, un framework modulaire permettant le déploiement de cas d'usage d'inspection visuelle.

Exemple de Usecase: vérifier la qualité de produits assemblés sur une chaîne de production industrielle.

## Contexte

### VIO un framework MLOPS

Le framework VIO a été pensé pour accélérer le déploiement d'un usecase d'inspection visuelle et proposé un cadre sur les différentes briques du MLOPS que sont:

- La collection de donnée (data gathering)
- la supervision de modèles (model monitoring)
- Le réentrainnement de modèles (model factory)
- Le management d'une flotte d'edges (Fleet Management)
- Le déploiement de software (software factory)

 ![vio-mlops](images/vio_mlops.png)

Voilà un aperçu de la stack d'une implémentation de VIO déployé sur le cloud azure:
 
 ![vio-architecture-stack](images/vio_azure_stack.png)
 

### L'approche micro-service

Les sous-dossiers du dossier courant, à savoir :

- [le core de l'orchestration](supervisor.md) 
- [l'interface à l'edge](edge_interface.md)
- [l'instance de serving de modèles](model_serving.md)
- [le monitoring de la flotte](monitoring.md)
- [les outils de déploiement](deployment.md)

sont chacun un module, une application, un micro-service indépendant. Chacun d'eux est donc fonctionnel seul (modulo une BD pour supervisor).

Ces micro-services (ou modules ou applications) sont tous (ou presque) packagés sous forme d'image Docker pour faciliter leur déploiement.

### Un framework modulaire

Le core de VIO a été construit en respectant les guidelines de l'architecture hexagonale, ce qui lui permet d'être modulaire et adaptable aux contraintes dans lequel il sera amené à être déployé

![vio-hexagonal-architecture](images/vio_hexagonal_architecture.png)

## Utilisation

Pour pouvoir lancer la stack complète, la dépendance minimale et suffisante est docker.

### Lancer la stack complète avec le Makefile

Pour lancer l'ensemble de la stack, le [Makefile](../Makefile) définit des targets, s'appuyant sur le [docker-compose.yml](../docker-compose.yml), permettant de :

- lancer tous les services (supervisor, model-serving, Mongo DB, UI) : `make services-up`
- lancer le supervisor conteneurisé : `make supervisor`
- lancer le model-serving conteneurisé : `make model_serving`
- lancer l'ui conteneurisé : `make ui`
- arrêter et supprimer tous les services : `make services-down`

Chacune des targets précédentes correspond à une commande [docker-compose.yml](../docker-compose.yml).

Par exemple, la target `supervisor` correspond à :

```shell
$ docker-compose up -d --build supervisor
```


### Lancer la stack complète avec des commandes docker-compose

Un autre moyen de lancer toute la stack en une commande est le suivant :

```shell
$ docker-compose up -d --build
```

Celle-ci lance tous les services de la stack définis dans le [docker-compose.yml](../docker-compose.yml). On peut ensuite les arrêter tous avec la commande (les containers seront arrêtés et supprimés) :

```shell
$ docker-compose down
```
