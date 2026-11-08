"""Bounded bridge from personal tasks to OpenJarvis coding agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .permissions import PermissionAuditLog, PermissionPolicy
from .runner import BoundedRunner, RunnerLimits, Step
from .tasks import Task, TaskStore


class AutonomousCodingService:
    """Run a coding request through the existing secured agent executor."""

    def __init__(
        self,
        db_path: str | Path,
        executor: Any,
        *,
        limits: RunnerLimits | None = None,
    ) -> None:
        self._store = TaskStore(db_path)
        self._executor = executor
        audit = PermissionAuditLog(db_path)
        policy = PermissionPolicy(
            audit,
            allowed_capabilities={"code:execute", "file:read", "file:write"},
        )
        self._runner = BoundedRunner(self._store, policy, limits=limits)

    def run(self, prompt: str, *, workspace: str = "") -> tuple[str, Any]:
        task = self._store.create(
            prompt,
            metadata={"kind": "autonomous_coding", "workspace": workspace},
        )
        result: dict[str, Any] = {}

        def execute() -> dict[str, Any]:
            response = self._executor.run_ephemeral(
                "native_openhands",
                (
                    "You are JARVIS coding mode. Work only in the requested workspace, "
                    "make the smallest safe change, run relevant tests, and report "
                    "files changed."
                ),
                f"Workspace: {workspace}\n\nTask: {prompt}",
                ["file_read", "file_write", "shell_exec"],
            )
            if isinstance(response, dict):
                result.update(response)
            else:
                result["content"] = getattr(response, "content", str(response))
            return result

        self._runner.run(task.id, lambda: Step("code:execute", execute))
        return task.id, result

    def get_task(self, task_id: str) -> Task | None:
        return self._store.get(task_id)


__all__ = ["AutonomousCodingService"]
