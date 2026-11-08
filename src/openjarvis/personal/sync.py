"""Offline-first, user-controlled event sync for personal JARVIS data."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any


class OfflineSyncStore:
    """Keep a durable outbox and exchange deduplicated JSON bundles."""

    def __init__(self, path: Path, *, device_id: str) -> None:
        self.device_id = device_id.strip()
        if not self.device_id:
            raise ValueError("device_id is required")
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS sync_events "
            "(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL)"
        )
        self._db.commit()

    def record(self, kind: str, payload: dict[str, Any]) -> str:
        event_id = f"{self.device_id}:{uuid.uuid4().hex}"
        self._db.execute(
            "INSERT INTO sync_events(id, kind, payload) VALUES (?, ?, ?)",
            (event_id, kind.strip(), json.dumps(payload, sort_keys=True)),
        )
        self._db.commit()
        return event_id

    def pending(self) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT id, kind, payload FROM sync_events ORDER BY id"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "kind": row["kind"],
                "payload": json.loads(row["payload"]),
            }
            for row in rows
        ]

    def export_bundle(self) -> str:
        return json.dumps(
            {"version": 1, "device_id": self.device_id, "events": self.pending()},
            sort_keys=True,
        )

    def import_bundle(self, bundle: str) -> int:
        data = json.loads(bundle)
        if data.get("version") != 1 or not isinstance(data.get("events"), list):
            raise ValueError("unsupported sync bundle")
        added = 0
        for event in data["events"]:
            if not all(key in event for key in ("id", "kind", "payload")):
                raise ValueError("malformed sync event")
            cursor = self._db.execute(
                "INSERT OR IGNORE INTO sync_events(id, kind, payload) VALUES (?, ?, ?)",
                (
                    event["id"],
                    event["kind"],
                    json.dumps(event["payload"], sort_keys=True),
                ),
            )
            added += cursor.rowcount
        self._db.commit()
        return added

    def close(self) -> None:
        self._db.close()


__all__ = ["OfflineSyncStore"]
