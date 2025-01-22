from typing import Dict, List, Optional

from pydantic import BaseModel

from models.use_case import UseCase


class Edge(BaseModel):
    name: str
    edge_ip: Optional[str] = None
    use_cases_names: Optional[List[str]] = []
    use_cases: Optional[Dict[str, UseCase]] = {}

    def add_usecase(self, use_case: str, edge_ip: str):
        self.edge_ip = edge_ip
        self.use_cases_names.append(use_case)
        self.use_cases[use_case] = UseCase()
