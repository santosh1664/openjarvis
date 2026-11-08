"""User-owned preferences layered on OpenJarvis's durable fact store."""

from __future__ import annotations

from openjarvis.memory.store import TRUST_TRUSTED, FactStore


class PersonalMemory:
    """Persist explicit user preferences with trusted provenance."""

    _PREFIX = "personal-preference"

    def __init__(self, store: FactStore) -> None:
        self._store = store

    def remember(self, key: str, value: str) -> bool:
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return False
        return self._store.add_with_trust(
            f"{self._PREFIX}:{key}={value}",
            source="personal-preference",
            trust=TRUST_TRUSTED,
        )

    def get(self, key: str) -> str | None:
        prefix = f"{self._PREFIX}:{key.strip()}="
        for fact in reversed(self._store.list()):
            if fact.trust not in ("", TRUST_TRUSTED):
                continue
            if fact.text.startswith(prefix):
                return fact.text[len(prefix) :]
        return None


__all__ = ["PersonalMemory"]
