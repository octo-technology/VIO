# Documentation

To update the documentation, feel free to modify / add markdown file in the `/docs` folder of the repository

## Preview Locally

To build locally your github pages site

```shell
$ mkdocs build
```

To test locally your github pages site

```shell
$ mkdocs serve
```

## Publish on github pages

Simply commit your modification on your branch, issue a PR and the
workflow [publication_pages_gh-pages_branch.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_pages_gh-pages_branch.yml)
will be triggered automatically.

Note: (Wrong behaviour) to manually push your modification directly to github pages you can execute the command:

```shell
$ mkdocs gh-deploy
```
