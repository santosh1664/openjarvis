# Personal JARVIS Foundation Design

## Goal

Add a small, local-first foundation for a personal JARVIS without replacing OpenJarvis components: durable tasks, deny-by-default permissions with an audit trail, and bounded autonomous execution.

## Scope

This milestone includes a reusable task abstraction, SQLite persistence, a permission policy boundary, an append-only decision log, a bounded runner, and tests. It does not add camera input, gestures, holograms, voice UX, or a new model/runtime.

## Architecture

The feature lives in a focused `openjarvis.personal` package. `TaskStore` owns SQLite schema and CRUD operations. `PermissionPolicy` evaluates requested capabilities against an explicit allowlist and sends every decision to `PermissionAuditLog`. `BoundedRunner` executes a caller-supplied step function while enforcing maximum steps, elapsed time, and consecutive failures. The components communicate through small dataclasses and protocols so they can later be used by the existing operative agent or scheduler without coupling this milestone to either one.

SQLite is the persistence format because OpenJarvis already uses SQLite, it is available in the supported Python environment, and it provides reliable restart behavior and indexed status queries. The default policy denies all capabilities; callers must explicitly provide allowed capabilities for a run. No existing upstream tool behavior changes unless a caller opts into the new policy boundary.

## Data flow

1. A caller creates a task with a stable id and receives a persisted `Task` record.
2. A runner loads the task, requests permission for each capability before performing a step, and records the decision with task id, capability, outcome, and reason.
3. The runner updates task status after each transition and persists the final result, failure, or bound-exceeded reason.
4. A restarted process can reload pending/running tasks and inspect the audit trail without relying on in-memory state.

## Safety and failure behavior

- Empty or missing allowlists deny every capability.
- Unknown capabilities are denied and logged.
- A denied action does not execute its step.
- The runner stops when it reaches the step, time, or failure bound and marks the task accordingly.
- SQLite writes use transactions; malformed task ids or invalid status transitions raise clear validation errors.
- Audit entries exclude arbitrary payloads and store only bounded metadata needed to explain the decision.

## Testing

Tests will cover task round-trips and restart persistence, default denial, explicit allow, unknown-capability denial, audit records, step/time/failure bounds, and a permitted end-to-end task run. Existing upstream tests will be run unchanged, plus formatting/type checks applicable to the touched files.

## Follow-on roadmap

After this milestone, a separate change can connect the foundation to the operative agent and scheduler, then add a reviewed one-command setup flow (`jarvis setup --full`) that initializes the local database and restrictive defaults. Autonomous coding tools should be integrated only after the permission boundary is exercised by real tool calls. Camera, gestures, and hologram work remain reserved for the explicitly requested “Final Phase.”
