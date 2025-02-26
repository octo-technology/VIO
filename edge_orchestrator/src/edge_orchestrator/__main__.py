from edge_orchestrator.interface.api.main import app


def run_for_debug():
    import uvicorn

    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")


if __name__ == "__main__":
    run_for_debug()
