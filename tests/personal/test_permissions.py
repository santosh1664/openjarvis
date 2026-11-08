from __future__ import annotations

from openjarvis.personal.permissions import PermissionAuditLog, PermissionPolicy


def test_policy_denies_by_default_and_persists_decision(tmp_path):
    audit = PermissionAuditLog(tmp_path / "audit.db")
    policy = PermissionPolicy(audit)

    decision = policy.check("task-1", "code:execute")

    assert not decision.allowed
    assert audit.list(task_id="task-1")[0].reason == "capability not allowed"


def test_policy_allows_explicit_capability(tmp_path):
    audit = PermissionAuditLog(tmp_path / "audit.db")
    policy = PermissionPolicy(audit, allowed_capabilities={"file:read"})

    assert policy.check("task-1", "file:read").allowed
    assert not policy.check("task-1", "network:write").allowed


def test_decision_can_gate_existing_tool_executor(tmp_path):
    audit = PermissionAuditLog(tmp_path / "audit.db")
    policy = PermissionPolicy(audit, allowed_capabilities={"file:read"})

    assert bool(policy.check("agent-1", "file:read", "file_read"))
    assert not bool(policy.check("agent-1", "file:write", "file_write"))
