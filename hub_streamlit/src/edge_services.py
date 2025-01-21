from typing import Optional

import requests
from requests import exceptions


def get_active_config(edge_ip: str) -> Optional[dict]:
    try:
        response = requests.get(
            f"http://{edge_ip}:8000/api/v1/configs/active", timeout=1
        )
        return response.json()
    except exceptions as e:
        print(e)
        return False
