"""Persistent personal task records backed by SQLite."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    title: str
    status: TaskStatus
    created_at: str
    updated_at: str
    metadata: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStore:
    """SQLite persistence for personal task lifecycle state."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS personal_tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL,
                result TEXT,
                error TEXT
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_personal_tasks_status "
            "ON personal_tasks(status)"
        )
        self._conn.commit()

    def create(self, title: str, *, metadata: dict[str, Any] | None = None) -> Task:
        if not title.strip():
            raise ValueError("task title must not be empty")
        now = _now()
        task = Task(
            id=uuid.uuid4().hex,
            title=title,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self._conn.execute(
            "INSERT INTO personal_tasks "
            "(id, title, status, created_at, updated_at, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                task.id,
                task.title,
                task.status.value,
                now,
                now,
                json.dumps(task.metadata),
            ),
        )
        self._conn.commit()
        return task

    def get(self, task_id: str) -> Task | None:
        row = self._conn.execute(
            "SELECT id, title, status, created_at, updated_at, metadata, result, error "
            "FROM personal_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return self._from_row(row) if row else None

    def list(self, status: TaskStatus | str | None = None) -> list[Task]:
        query = (
            "SELECT id, title, status, created_at, updated_at, metadata, result, error "
            "FROM personal_tasks"
        )
        params: tuple[str, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (TaskStatus(status).value,)
        query += " ORDER BY updated_at DESC"
        return [self._from_row(row) for row in self._conn.execute(query, params)]

    def update(
        self,
        task_id: str,
        *,
        status: TaskStatus | str | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Task:
        task = self.get(task_id)
        if task is None:
            raise KeyError(f"unknown task: {task_id}")
        if status is not None:
            try:
                status = TaskStatus(status)
            except ValueError as exc:
                raise ValueError(f"invalid task status: {status}") from exc
        new_status = status or task.status
        updated = _now()
        self._conn.execute(
            "UPDATE personal_tasks SET status = ?, updated_at = ?, "
            "result = ?, error = ? "
            "WHERE id = ?",
            (
                new_status.value,
                updated,
                json.dumps(result)
                if result is not None
                else (json.dumps(task.result) if task.result is not None else None),
                error if error is not None else task.error,
                task_id,
            ),
        )
        self._conn.commit()
        return self.get(task_id)  # type: ignore[return-value]

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _from_row(row: tuple[Any, ...]) -> Task:
        return Task(
            id=row[0],
            title=row[1],
            status=TaskStatus(row[2]),
            created_at=row[3],
            updated_at=row[4],
            metadata=json.loads(row[5]),
            result=json.loads(row[6]) if row[6] else None,
            error=row[7],
        )


__all__ = ["Task", "TaskStatus", "TaskStore"]
