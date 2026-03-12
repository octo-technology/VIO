from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from edge_orchestrator.domain.models.inspection_event import InspectionEvent


class IInspectionQueue(ABC):
    @abstractmethod
    async def enqueue(self, station_name: str) -> InspectionEvent: ...

    @abstractmethod
    async def dequeue(self) -> Optional[InspectionEvent]: ...

    @abstractmethod
    async def mark_done(self, event_id: UUID) -> None: ...

    @abstractmethod
    async def mark_failed(self, event_id: UUID, error: str) -> None: ...

    @abstractmethod
    async def recover_interrupted(self) -> int:
        """Reset RUNNING → PENDING at startup. Returns count of recovered events."""
