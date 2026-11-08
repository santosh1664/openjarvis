"""Local passcode gate for sensitive JARVIS actions."""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import time
from pathlib import Path


class PasscodeStore:
    """Store only a salted scrypt hash and enforce temporary lockout."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        max_failures: int = 5,
        lock_seconds: int = 60,
    ) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._max_failures = max(1, max_failures)
        self._lock_seconds = max(1, lock_seconds)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS security_passcode "
            "(id INTEGER PRIMARY KEY CHECK(id = 1), salt BLOB NOT NULL, "
            "digest BLOB NOT NULL, failures INTEGER NOT NULL DEFAULT 0, "
            "locked_until REAL NOT NULL DEFAULT 0)"
        )
        self._conn.commit()

    def set_passcode(self, passcode: str) -> None:
        if len(passcode) < 4 or len(passcode) > 128:
            raise ValueError("passcode must be between 4 and 128 characters")
        salt = os.urandom(16)
        digest = self._derive(passcode, salt)
        self._conn.execute(
            "INSERT INTO security_passcode(id, salt, digest) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET salt=excluded.salt, digest=excluded.digest, "
            "failures=0, locked_until=0",
            (salt, digest),
        )
        self._conn.commit()

    def is_configured(self) -> bool:
        return (
            self._conn.execute(
                "SELECT 1 FROM security_passcode WHERE id = 1"
            ).fetchone()
            is not None
        )

    def verify(self, passcode: str) -> bool:
        row = self._conn.execute(
            "SELECT salt, digest, failures, locked_until FROM security_passcode "
            "WHERE id = 1"
        ).fetchone()
        if row is None:
            return False
        salt, expected, failures, locked_until = row
        now = time.time()
        if locked_until > now:
            return False
        candidate = self._derive(passcode, salt)
        if hmac.compare_digest(candidate, expected):
            self._conn.execute(
                "UPDATE security_passcode SET failures = 0, locked_until = 0 "
                "WHERE id = 1"
            )
            self._conn.commit()
            return True
        failures += 1
        lock_until = now + self._lock_seconds if failures >= self._max_failures else 0
        self._conn.execute(
            "UPDATE security_passcode SET failures = ?, locked_until = ? WHERE id = 1",
            (failures, lock_until),
        )
        self._conn.commit()
        return False

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _derive(passcode: str, salt: bytes) -> bytes:
        return hashlib.scrypt(
            passcode.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
        )


__all__ = ["PasscodeStore"]
