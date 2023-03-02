# The CICD

We use Github Actions workflows for continuous integration and continuous deployment.

## The continuous integration workflows

- [ci_edge_interface.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/ci_edge_interface.yml): the
  CI of the edge_interface application is decomposed into 2 jobs

        job lint_and_test_on_edge_interface: static code analysis of JavaScript code (no tests at the moment)
        job build_and_push_images: building the Docker image of the application without publishing to a registry

- [ci_edge_orchestrator.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/ci_edge_orchestrator.yml):
  the CI of the edge_orchestrator application is decomposed into 2 jobs

        job lint_and_test_on_edge_orchestrator: static code analysis with Flake8 followed by automated tests (unit, integration, and functional) with storing test reports in Github
        job build_and_push_images: building the Docker image of the application without publishing to a registry

The CI workflows (edge_[interface|orchestrator]_ci.yml) are triggered under one of the following conditions:

- if a merge request with differences is opened on Github
- if a commit on the master branch is pushed to Github

## The release workflows

- [publication_vio_images.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_vio_images.yml):
  publication of Docker edge_serving images by manual trigger job

        build_and_push_images: building Docker images with publishing images to the Github registry  

- [publication_vio_images_raspberry.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_vio_images_raspberry.yml):
  publication of Docker edge_serving images by manual trigger job

        build_and_push_images: building Docker images specific to Raspberry hardware with publishing images to the Github registry

- [publication_pages_gh-pages_branch.yml](https://github.com/octo-technology/VIO/tree/main/.github/workflows/publication_pages_gh-pages_branch.yml):
  generation and deployment of documentation

The release workflows are triggered under one of the following conditions:

- if a release is created from Github
