"""Bounded local suggestions for a proactive personal assistant."""

from __future__ import annotations

from pathlib import Path

from .automation import PersonalAutomation
from .tasks import TaskStatus, TaskStore


class ProactiveAssistant:
    """Suggest next actions from local state without executing them."""

    def __init__(self, config_dir: Path) -> None:
        self._config_dir = config_dir

    def suggestions(self, *, limit: int = 10) -> list[str]:
        if limit < 1:
            return []
        suggestions: list[str] = []
        tasks = TaskStore(self._config_dir / "personal_tasks.db")
        automation = PersonalAutomation(self._config_dir / "scheduler.db")
        try:
            pending = tasks.list(TaskStatus.PENDING)
            failed = tasks.list(TaskStatus.FAILED)
            active = automation.list(status="active")
        finally:
            tasks.close()
            automation.close()
        suggestions.extend(f"Review pending task: {task.title}" for task in pending)
        suggestions.extend(
            f"Retry or inspect failed task: {task.title}" for task in failed
        )
        if active:
            suggestions.append(f"Review {len(active)} active automation(s)")
        return suggestions[:limit]


__all__ = ["ProactiveAssistant"]
