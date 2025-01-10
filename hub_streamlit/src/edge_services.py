import requests


def get_active_config(edge_ip: str):
    try:
        response = requests.get(f'http://{edge_ip}:8000/api/v1/configs/active', timeout=1)
        return response.json()
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException as e:
        print(e)