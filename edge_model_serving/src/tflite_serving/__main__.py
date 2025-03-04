from tflite_serving.tflite_server import app


def run_for_debug():
    import uvicorn

    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=8501, log_level="debug")


if __name__ == "__main__":
    run_for_debug()
