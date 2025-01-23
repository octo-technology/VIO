from typing import Dict, List, Optional

from pydantic import BaseModel

from models.use_case import UseCase


class Edge(BaseModel):
    name: str
    edge_ip: Optional[str] = None
    use_cases: List[UseCase] = []

    def add_usecase(self, use_case_name: str, edge_ip: str):
        self.edge_ip = edge_ip
        self.use_cases.append(UseCase(name=use_case_name))

    def get_use_case_names(self) -> List[str]:
        return [use_case.name for use_case in self.use_cases]
    
    def get_use_case(self, name: str) -> Optional[UseCase]:
        for use_case in self.use_cases:
            if use_case.name == name:
                return use_case
        return None