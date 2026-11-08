"""Bounded execution loop for explicitly permitted personal tasks."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable

from .permissions import PermissionPolicy
from .tasks import TaskStatus, TaskStore


@dataclass(frozen=True, slots=True)
class Step:
    capability: str
    action: Callable[[], Any]


class RunnerOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    DENIED = "denied"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RunnerLimits:
    max_steps: int = 10
    max_seconds: float = 60.0
    max_failures: int = 1

    def __post_init__(self) -> None:
        if self.max_steps < 1 or self.max_seconds <= 0 or self.max_failures < 1:
            raise ValueError("runner limits must be positive")


class BoundedRunner:
    def __init__(
        self,
        store: TaskStore,
        policy: PermissionPolicy,
        *,
        limits: RunnerLimits | None = None,
    ) -> None:
        self._store = store
        self._policy = policy
        self._limits = limits or RunnerLimits()

    def run(self, task_id: str, next_step: Callable[[], Step]) -> RunnerOutcome:
        self._store.update(task_id, status=TaskStatus.RUNNING)
        started = time.monotonic()
        failures = 0
        for index in range(self._limits.max_steps):
            if index and time.monotonic() - started >= self._limits.max_seconds:
                self._store.update(
                    task_id, status=TaskStatus.STOPPED, error="time limit exceeded"
                )
                return RunnerOutcome.STOPPED
            step = next_step()
            decision = self._policy.check(task_id, step.capability)
            if not decision.allowed:
                self._store.update(
                    task_id, status=TaskStatus.STOPPED, error=decision.reason
                )
                return RunnerOutcome.DENIED
            try:
                result = step.action()
            except Exception as exc:
                failures += 1
                if failures >= self._limits.max_failures:
                    self._store.update(
                        task_id, status=TaskStatus.FAILED, error=str(exc)
                    )
                    return RunnerOutcome.FAILED
                continue
            if result is not None:
                self._store.update(
                    task_id,
                    status=TaskStatus.SUCCEEDED,
                    result=result if isinstance(result, dict) else {"value": result},
                )
                return RunnerOutcome.SUCCEEDED
        self._store.update(
            task_id, status=TaskStatus.STOPPED, error="step limit exceeded"
        )
        return RunnerOutcome.STOPPED


__all__ = ["BoundedRunner", "RunnerLimits", "RunnerOutcome", "Step"]
