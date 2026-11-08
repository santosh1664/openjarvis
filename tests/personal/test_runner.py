from __future__ import annotations

from openjarvis.personal.permissions import PermissionAuditLog, PermissionPolicy
from openjarvis.personal.runner import BoundedRunner, RunnerLimits, RunnerOutcome, Step
from openjarvis.personal.tasks import TaskStatus, TaskStore


def make_runner(tmp_path, allowed=None, limits=None):
    store = TaskStore(tmp_path / "tasks.db")
    audit = PermissionAuditLog(tmp_path / "audit.db")
    policy = PermissionPolicy(audit, allowed_capabilities=allowed)
    return store, BoundedRunner(
        store, policy, limits=limits or RunnerLimits(max_steps=2)
    )


def test_runner_executes_permitted_step_and_persists_result(tmp_path):
    store, runner = make_runner(tmp_path, {"task:run"})
    task = store.create("Run it")
    result = runner.run(task.id, lambda: Step("task:run", lambda: {"ok": True}))
    assert result is RunnerOutcome.SUCCEEDED
    assert store.get(task.id).status is TaskStatus.SUCCEEDED


def test_runner_does_not_execute_denied_step(tmp_path):
    store, runner = make_runner(tmp_path)
    task = store.create("Do not run")
    called = False

    def action():
        nonlocal called
        called = True

    assert runner.run(task.id, lambda: Step("task:run", action)) is RunnerOutcome.DENIED
    assert not called


def test_runner_stops_at_step_bound(tmp_path):
    store, runner = make_runner(tmp_path, {"task:run"}, RunnerLimits(max_steps=1))
    task = store.create("Bounded")
    assert (
        runner.run(task.id, lambda: Step("task:run", lambda: None))
        is RunnerOutcome.STOPPED
    )
    assert store.get(task.id).status is TaskStatus.STOPPED


def test_runner_executes_multiple_steps_with_individual_permissions(tmp_path):
    store, runner = make_runner(tmp_path, {"file:read", "file:write"})
    task = store.create("Two steps")
    calls: list[str] = []
    steps = iter(
        [
            Step("file:read", lambda: calls.append("read")),
            Step("file:write", lambda: {"calls": calls + ["write"]}),
        ]
    )

    outcome = runner.run(task.id, lambda: next(steps))

    assert outcome is RunnerOutcome.SUCCEEDED
    assert calls == ["read"]
    assert store.get(task.id).result == {"calls": ["read", "write"]}


def test_runner_stops_after_failure_limit(tmp_path):
    store, runner = make_runner(
        tmp_path, {"task:run"}, RunnerLimits(max_steps=3, max_failures=2)
    )
    task = store.create("Failing")

    def fail():
        raise RuntimeError("broken step")

    outcome = runner.run(task.id, lambda: Step("task:run", fail))

    assert outcome is RunnerOutcome.FAILED
    assert store.get(task.id).error == "broken step"
