"""Small local knowledge graph for explicit personal context."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class PersonalKnowledgeGraph:
    def __init__(self, path: Path) -> None:
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS entities (
                name TEXT PRIMARY KEY, kind TEXT NOT NULL, description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS relations (
                source TEXT NOT NULL, predicate TEXT NOT NULL, target TEXT NOT NULL,
                PRIMARY KEY (source, predicate, target)
            );
            """
        )
        self._db.commit()

    def upsert_entity(self, kind: str, name: str, description: str = "") -> None:
        kind, name, description = kind.strip(), name.strip(), description.strip()
        if not kind or not name:
            raise ValueError("entity kind and name are required")
        self._db.execute(
            "INSERT INTO entities(name, kind, description) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET kind=excluded.kind, "
            "description=excluded.description",
            (name, kind, description),
        )
        self._db.commit()

    def link(self, source: str, predicate: str, target: str) -> None:
        values = tuple(value.strip() for value in (source, predicate, target))
        if not all(values):
            raise ValueError("source, predicate, and target are required")
        self._db.execute(
            "INSERT OR IGNORE INTO relations(source, predicate, target) "
            "VALUES (?, ?, ?)",
            values,
        )
        self._db.commit()

    def find(self, text: str) -> list[dict[str, str]]:
        rows = self._db.execute(
            "SELECT name, kind, description FROM entities "
            "WHERE name LIKE ? OR description LIKE ? ORDER BY name",
            (f"%{text.strip()}%", f"%{text.strip()}%"),
        ).fetchall()
        return [dict(row) for row in rows]

    def related(self, source: str) -> list[tuple[str, str]]:
        rows = self._db.execute(
            "SELECT predicate, target FROM relations "
            "WHERE source = ? ORDER BY predicate, target",
            (source.strip(),),
        ).fetchall()
        return [(row["predicate"], row["target"]) for row in rows]

    def links_touching(self, name: str) -> list[tuple[str, str, str]]:
        rows = self._db.execute(
            "SELECT source, predicate, target FROM relations "
            "WHERE source = ? OR target = ? ORDER BY source, predicate, target",
            (name.strip(), name.strip()),
        ).fetchall()
        return [(row["source"], row["predicate"], row["target"]) for row in rows]

    def close(self) -> None:
        self._db.close()


__all__ = ["PersonalKnowledgeGraph"]
