# Azure Postgresql Migration

[[_TOC_]]

## Alembic migration
To run Postgresql migration we use [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

You need to install alembic (inside [requirements.txt](../../../deployment/requirements.txt)) as follow:
```shell scrip
$ cd ./deployment/
$ conda activate ansible
$ pip install -r requirements.txt
```

### Add migration script
To create a migration, type:
```shell script
$ cd ./deployment/ansible/
$ alembic revision -m "Add a column"
```

A new file is generated in the directory `alembic/versions` and you are good to write your migration.


### Run migration script
Before running a migration, you can check what is currently deployed:
```shell script
$ alembic current
```

Then, you can run the command:
```shell script
$ alembic upgrade head
```
