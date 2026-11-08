"""Explicit capability checks with a durable audit trail."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PermissionDecision:
    task_id: str
    capability: str
    allowed: bool
    reason: str
    created_at: str

    def __bool__(self) -> bool:
        """Allow decisions to plug into OpenJarvis's existing policy gate."""
        return self.allowed


class PermissionAuditLog:
    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS permission_audit "
            "(task_id TEXT NOT NULL, capability TEXT NOT NULL, "
            "allowed INTEGER NOT NULL, "
            "reason TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        self._conn.commit()

    def record(self, decision: PermissionDecision) -> None:
        self._conn.execute(
            "INSERT INTO permission_audit VALUES (?, ?, ?, ?, ?)",
            (
                decision.task_id,
                decision.capability,
                int(decision.allowed),
                decision.reason[:256],
                decision.created_at,
            ),
        )
        self._conn.commit()

    def list(self, *, task_id: str | None = None) -> list[PermissionDecision]:
        query = (
            "SELECT task_id, capability, allowed, reason, created_at "
            "FROM permission_audit"
        )
        args: tuple[str, ...] = ()
        if task_id is not None:
            query += " WHERE task_id = ?"
            args = (task_id,)
        query += " ORDER BY rowid"
        return [
            PermissionDecision(row[0], row[1], bool(row[2]), row[3], row[4])
            for row in self._conn.execute(query, args)
        ]

    def close(self) -> None:
        self._conn.close()


class PermissionPolicy:
    def __init__(
        self,
        audit_log: PermissionAuditLog,
        *,
        allowed_capabilities: set[str] | None = None,
    ) -> None:
        self._audit = audit_log
        self._allowed = frozenset(allowed_capabilities or ())

    def check(
        self,
        task_id: str,
        capability: str,
        tool_name: str | None = None,
    ) -> PermissionDecision:
        if not capability.strip():
            allowed = False
            reason = "capability is empty"
        elif capability in self._allowed:
            allowed = True
            reason = "capability explicitly allowed"
        else:
            allowed = False
            reason = "capability not allowed"
        if tool_name:
            reason = f"{reason} (tool: {tool_name})"
        decision = PermissionDecision(
            task_id, capability, allowed, reason, datetime.now(timezone.utc).isoformat()
        )
        self._audit.record(decision)
        return decision


__all__ = ["PermissionAuditLog", "PermissionDecision", "PermissionPolicy"]
