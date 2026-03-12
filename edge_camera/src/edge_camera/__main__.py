import uvicorn

from edge_camera.interface.api.app import create_app


def run():
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8081)


if __name__ == "__main__":
    run()
