from typing import Optional

import requests
from requests.exceptions import RequestException, Timeout


def get_supervisor_active_config(edge_ip: str) -> Optional[dict]:
    try:
        response = requests.get(
            f"http://{edge_ip}:8000/api/v1/configs/active", timeout=1
        )
        return response.json()
    except RequestException or Timeout as e:
        print(f"Error while fetching active config from {edge_ip}. Error: {e}")
        return None
