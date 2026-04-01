# edge_orchestrator

The edge_orchestrator orchestrates the following steps as soon as it is triggered:

1. image capture
2. image backup
3. metadata backup
4. model inference on images
5. saving results


## Building the Docker image

Depending on the target platform that will run the Docker container, we need to condition the Dockerfile accordingly.

Therefor, we use the `TARGETPLATFORM` variable that is the value set with `--platform` flag on build:
```bash
docker build --platform linux/arm64 .
```

Do not get confused with the `BUILDPLATFORM` variable, that matches the current machine. (e.g. linux/amd64 or MacOs).

Visit:
- [Multi-platform build arguments](https://docs.docker.com/build/building/variables/#multi-platform-build-arguments) for more details on Build variables
- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/) for more details on the Multi-platform build with Docker
