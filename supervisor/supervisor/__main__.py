import uvicorn

from supervisor.application.server import server

if __name__ == '__main__':
    uvicorn.run(server(), host="0.0.0.0", port=8000, log_level="info")
