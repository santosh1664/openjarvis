"""Three-profile conversation isolation and name-based routing."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Profile:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ProfileMessage:
    profile_id: str
    role: str
    content: str
    created_at: str


class ProfileStore:
    """SQLite-backed profile and per-profile conversation store."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS personal_profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profile_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES personal_profiles(id)
            );
            """
        )
        self._conn.commit()

    def create(self, name: str) -> Profile:
        name = name.strip()
        if not name:
            raise ValueError("profile name must not be empty")
        if len(self.list()) >= 3:
            raise ValueError("maximum of 3 profiles reached")
        profile = Profile(uuid.uuid4().hex, name)
        try:
            self._conn.execute(
                "INSERT INTO personal_profiles VALUES (?, ?, ?)",
                (profile.id, profile.name, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"profile already exists: {name}") from exc
        return profile

    def list(self) -> list[Profile]:
        rows = self._conn.execute(
            "SELECT id, name FROM personal_profiles ORDER BY created_at"
        )
        return [Profile(row[0], row[1]) for row in rows]

    def get(self, profile_id: str) -> Profile | None:
        row = self._conn.execute(
            "SELECT id, name FROM personal_profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        return Profile(row[0], row[1]) if row else None

    def by_name(self, name: str) -> Profile | None:
        row = self._conn.execute(
            "SELECT id, name FROM personal_profiles WHERE name = ?", (name.strip(),)
        ).fetchone()
        return Profile(row[0], row[1]) if row else None

    def add_message(self, profile_id: str, role: str, content: str) -> None:
        if self.get(profile_id) is None:
            raise KeyError(f"unknown profile: {profile_id}")
        self._conn.execute(
            "INSERT INTO profile_messages(profile_id, role, content, created_at) "
            "VALUES (?, ?, ?, ?)",
            (profile_id, role, content, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def messages(self, profile_id: str, limit: int = 100) -> list[ProfileMessage]:
        rows = self._conn.execute(
            "SELECT profile_id, role, content, created_at FROM profile_messages "
            "WHERE profile_id = ? ORDER BY id DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
        return [ProfileMessage(*row) for row in reversed(rows)]

    def match_address(self, text: str) -> str | None:
        normalized = text.strip()
        for profile in self.list():
            if normalized.casefold().startswith(profile.name.casefold() + ","):
                return profile.name
            if normalized.casefold().startswith(profile.name.casefold() + ":"):
                return profile.name
        return None

    def route(self, text: str) -> tuple[Profile | None, str]:
        """Return the addressed profile and input with the address removed."""
        normalized = text.strip()
        name = self.match_address(normalized)
        if name is None:
            return None, text
        profile = self.by_name(name)
        if profile is None:
            return None, text
        return profile, normalized[len(profile.name) :].lstrip(" ,:").strip()

    def close(self) -> None:
        self._conn.close()


__all__ = ["Profile", "ProfileMessage", "ProfileStore"]
