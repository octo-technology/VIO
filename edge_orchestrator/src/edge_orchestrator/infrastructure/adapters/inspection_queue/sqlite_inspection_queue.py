from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiosqlite

from edge_orchestrator.domain.models.inspection_event import (
    InspectionEvent,
    InspectionEventStatus,
)
from edge_orchestrator.domain.ports.inspection_queue.i_inspection_queue import (
    IInspectionQueue,
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS inspection_queue (
    id          TEXT PRIMARY KEY,
    item_id     TEXT NOT NULL,
    station_name TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error       TEXT
)
"""

_PRAGMA_WAL = "PRAGMA journal_mode=WAL"


class SqliteInspectionQueue(IInspectionQueue):
    def __init__(self, db_path: Path):
        self._db_path = str(db_path)
        self._conn: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute(_PRAGMA_WAL)
        await self._conn.execute(_CREATE_TABLE)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def enqueue(self, station_name: str) -> InspectionEvent:
        event = InspectionEvent(station_name=station_name)
        now = datetime.now().isoformat()
        await self._conn.execute(
            "INSERT INTO inspection_queue (id, item_id, station_name, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(event.id), str(event.item_id), station_name, InspectionEventStatus.PENDING, now, now),
        )
        await self._conn.commit()
        return event

    async def dequeue(self) -> Optional[InspectionEvent]:
        now = datetime.now().isoformat()
        async with self._conn.execute(
            "SELECT id, item_id, station_name, status, created_at, updated_at, retry_count, error "
            "FROM inspection_queue WHERE status = ? ORDER BY created_at LIMIT 1",
            (InspectionEventStatus.PENDING,),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return None

        await self._conn.execute(
            "UPDATE inspection_queue SET status = ?, updated_at = ? WHERE id = ?",
            (InspectionEventStatus.RUNNING, now, row["id"]),
        )
        await self._conn.commit()

        return InspectionEvent(
            id=UUID(row["id"]),
            item_id=UUID(row["item_id"]),
            station_name=row["station_name"],
            status=InspectionEventStatus.RUNNING,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(now),
            retry_count=row["retry_count"],
            error=row["error"],
        )

    async def mark_done(self, event_id: UUID) -> None:
        now = datetime.now().isoformat()
        await self._conn.execute(
            "UPDATE inspection_queue SET status = ?, updated_at = ? WHERE id = ?",
            (InspectionEventStatus.DONE, now, str(event_id)),
        )
        await self._conn.commit()

    async def mark_failed(self, event_id: UUID, error: str) -> None:
        now = datetime.now().isoformat()
        await self._conn.execute(
            "UPDATE inspection_queue SET status = ?, updated_at = ?, error = ? WHERE id = ?",
            (InspectionEventStatus.FAILED, now, error, str(event_id)),
        )
        await self._conn.commit()

    async def recover_interrupted(self) -> int:
        now = datetime.now().isoformat()
        async with self._conn.execute(
            "UPDATE inspection_queue SET status = ?, updated_at = ? WHERE status = ? RETURNING id",
            (InspectionEventStatus.PENDING, now, InspectionEventStatus.RUNNING),
        ) as cursor:
            rows = await cursor.fetchall()
        await self._conn.commit()
        return len(rows)
