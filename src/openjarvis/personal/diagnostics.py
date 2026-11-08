"""Safe local health checks and repairs for personal JARVIS state."""

from __future__ import annotations

import os
from pathlib import Path

from .providers import ProviderRouter


class PersonalDiagnostics:
    """Inspect local state and repair only deterministic, safe issues."""

    def __init__(self, config_dir: Path) -> None:
        self._config_dir = config_dir

    def run(self, *, repair: bool = False) -> dict[str, object]:
        repaired: list[str] = []
        if not self._config_dir.exists() and repair:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            repaired.append("config_dir")
        config_ready = self._config_dir.is_dir()
        permissions = (
            "private"
            if config_ready and os.name == "nt"
            else "private"
            if config_ready and (self._config_dir.stat().st_mode & 0o077) == 0
            else "review"
        )
        return {
            "config_dir": "ready" if config_ready else "missing",
            "config_permissions": permissions,
            "providers": {
                name: bool(info["configured"])
                for name, info in ProviderRouter().status().items()
            },
            "repaired": repaired,
        }


__all__ = ["PersonalDiagnostics"]
