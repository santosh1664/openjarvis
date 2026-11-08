# Personal JARVIS Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add durable personal tasks, deny-by-default permission auditing, and bounded autonomous execution without changing upstream agent/tool behavior.

**Architecture:** Create a focused `openjarvis.personal` package. A SQLite-backed `TaskStore` persists task state; `PermissionPolicy` and `PermissionAuditLog` make capability decisions explicit and auditable; `BoundedRunner` coordinates permitted steps under step, time, and failure limits.

**Tech Stack:** Python 3.10+, stdlib `sqlite3`, dataclasses, pytest, ruff.

---

### Task 1: Add task data model and SQLite store

**Files:**
- Create: `src/openjarvis/personal/__init__.py`
- Create: `src/openjarvis/personal/tasks.py`
- Test: `tests/personal/test_tasks.py`

- [ ] **Step 1: Write failing tests** for creating a task, retrieving it after reopening the database, updating status/result, and rejecting invalid status values.
- [ ] **Step 2: Run `uv run pytest tests/personal/test_tasks.py -q` and verify it fails because the package does not exist.**
- [ ] **Step 3: Implement `Task`, `TaskStatus`, and `TaskStore` with a WAL SQLite connection, schema creation, transactional create/get/update/list methods, UTC ISO timestamps, and JSON metadata/result fields.
- [ ] **Step 4: Run the focused tests and verify they pass.**
- [ ] **Step 5: Commit `feat: add persistent personal tasks`.**

### Task 2: Add deny-by-default policy and audit log

**Files:**
- Create: `src/openjarvis/personal/permissions.py`
- Test: `tests/personal/test_permissions.py`

- [ ] **Step 1: Write failing tests** showing empty policy denial, explicit capability allow, unknown capability denial, and persisted audit entries containing task id, capability, decision, and reason.
- [ ] **Step 2: Run `uv run pytest tests/personal/test_permissions.py -q` and verify the expected missing-module failure.**
- [ ] **Step 3: Implement `PermissionDecision`, `PermissionAuditLog`, and `PermissionPolicy`; default to an empty allowlist, validate non-empty capability names, use parameterized SQLite statements, and bound reason length.
- [ ] **Step 4: Run focused permission tests and verify they pass.**
- [ ] **Step 5: Commit `feat: add audited deny-by-default permissions`.**

### Task 3: Add bounded autonomous runner

**Files:**
- Create: `src/openjarvis/personal/runner.py`
- Test: `tests/personal/test_runner.py`

- [ ] **Step 1: Write failing tests** for a permitted successful run, denied capability preventing execution, maximum-step termination, consecutive-failure termination, and elapsed-time termination.
- [ ] **Step 2: Run `uv run pytest tests/personal/test_runner.py -q` and verify the expected missing-module failure.**
- [ ] **Step 3: Implement `RunnerLimits`, `RunnerOutcome`, and `BoundedRunner`; check permission before each step, update the task store for running/succeeded/failed/stopped states, use a monotonic clock, and never retry beyond the configured failure bound.
- [ ] **Step 4: Run focused runner tests and verify they pass.**
- [ ] **Step 5: Commit `feat: add bounded personal task runner`.**

### Task 4: Package exports and documentation

**Files:**
- Modify: `src/openjarvis/personal/__init__.py`
- Create: `docs/personal-jarvis-foundation.md`
- Test: `tests/personal/test_public_api.py`

- [ ] **Step 1: Write a failing public-API test** importing the task, permission, and runner types from `openjarvis.personal`.
- [ ] **Step 2: Run the focused test and verify the missing-export failure.**
- [ ] **Step 3: Export only the stable milestone types and document a minimal example using a temporary SQLite database and an explicit capability allowlist; state that camera, gestures, and holograms are deferred to Final Phase.
- [ ] **Step 4: Run the focused test and `uv run ruff check src/openjarvis/personal tests/personal`.**
- [ ] **Step 5: Commit `docs: expose personal jarvis foundation api`.**

### Task 5: Full verification

**Files:**
- Modify only if verification reveals a defect in the touched files.

- [ ] **Step 1: Run `uv run pytest tests/personal -q`.**
- [ ] **Step 2: Run the existing adjacent suites `uv run pytest tests/tools tests/agents tests/connectors/test_scheduler.py -q`.
- [ ] **Step 3: Run `uv run ruff check src/openjarvis/personal tests/personal` and inspect `git diff main...HEAD` to confirm upstream files were preserved.
- [ ] **Step 4: Record exact test counts, lint result, branch name, commits, and any known follow-on work in the final handoff.
