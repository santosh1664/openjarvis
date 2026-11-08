# Personal JARVIS foundation

The `openjarvis.personal` package provides a small local-first task foundation:

```python
from openjarvis.personal import (
    BoundedRunner,
    PermissionAuditLog,
    PermissionPolicy,
    RunnerLimits,
    Step,
    TaskStore,
)

store = TaskStore("jarvis.db")
audit = PermissionAuditLog("jarvis.db")
policy = PermissionPolicy(audit, allowed_capabilities={"notes:write"})
task = store.create("Save a note")
runner = BoundedRunner(store, policy, limits=RunnerLimits(max_steps=3))
runner.run(task.id, lambda: Step("notes:write", lambda: {"saved": True}))
```

The policy denies every capability unless it is explicitly allowlisted and records each decision. The runner stops at its step, time, or failure bounds. This milestone is intentionally independent of the existing agents and scheduler so upstream components remain unchanged.

Camera input, gestures, and hologram integration are deferred until the explicitly requested “Final Phase.”
