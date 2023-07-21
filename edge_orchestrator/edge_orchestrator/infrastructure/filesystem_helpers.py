from pathlib import Path


def get_tmp_path() -> Path:
    tmp_path = Path("/tmp/vio/edge_orchestrator/data/storage")
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path
