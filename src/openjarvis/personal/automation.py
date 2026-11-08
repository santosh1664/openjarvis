"""Personal automation facade over OpenJarvis's scheduler store."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from openjarvis.scheduler.scheduler import TaskScheduler
from openjarvis.scheduler.store import SchedulerStore


class PersonalAutomation:
    """Persist safe recurring automations for the existing scheduler runtime."""

    def __init__(self, db_path: str | Path) -> None:
        self._store = SchedulerStore(db_path)
        self._scheduler = TaskScheduler(self._store)

    def create(
        self,
        prompt: str,
        *,
        schedule_type: str,
        schedule_value: str,
        agent: str = "operative",
        tools: str = "",
    ) -> dict[str, Any]:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        self._validate_schedule(schedule_type, schedule_value)
        task = self._scheduler.create_task(
            prompt.strip(),
            schedule_type,
            schedule_value,
            agent=agent,
            tools=tools,
            context_mode="isolated",
            metadata={"managed_by": "personal_jarvis"},
        )
        return task.to_dict()

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        return [task.to_dict() for task in self._scheduler.list_tasks(status=status)]

    def close(self) -> None:
        self._store.close()

    @staticmethod
    def _validate_schedule(schedule_type: str, schedule_value: str) -> None:
        if schedule_type not in {"cron", "interval", "once"}:
            raise ValueError("schedule type must be cron, interval, or once")
        if not schedule_value.strip():
            raise ValueError("schedule value must not be empty")
        if schedule_type == "interval":
            try:
                if float(schedule_value) <= 0:
                    raise ValueError
            except ValueError as exc:
                raise ValueError("interval schedule must be positive") from exc
        elif schedule_type == "cron":
            try:
                from croniter import croniter

                if not croniter.is_valid(schedule_value):
                    raise ValueError
            except (ImportError, ValueError) as exc:
                raise ValueError("invalid cron schedule") from exc
        else:
            try:
                datetime.fromisoformat(schedule_value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("once schedule must be ISO datetime") from exc


__all__ = ["PersonalAutomation"]
