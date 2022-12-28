import uvicorn

from edge_orchestrator.application.server import server

if __name__ == '__main__':
    orchestrator_app = server()
    uvicorn.run(orchestrator_app, host="0.0.0.0", port=8000, log_level="info")
