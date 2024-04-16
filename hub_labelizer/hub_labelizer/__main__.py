import os
import sys
import uvicorn
from dotenv import load_dotenv

sys.path.append(f"{__file__}/VIO/edge_orchestrator")
load_dotenv()

from hub_labelizer.application.server import server


def main():
    hub_labelizer_app = server()
    uvicorn.run(hub_labelizer_app, host="0.0.0.0", port=8100, log_level="info")


if __name__ == "__main__":
    main()
