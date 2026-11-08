from __future__ import annotations

import pytest

from openjarvis.personal.tasks import TaskStatus, TaskStore


def test_task_survives_store_reopen(tmp_path):
    db = tmp_path / "tasks.db"
    store = TaskStore(db)
    task = store.create("Back up notes", metadata={"source": "jarvis"})
    store.update(task.id, status=TaskStatus.RUNNING)
    store.update(task.id, status=TaskStatus.SUCCEEDED, result={"files": 3})
    store.close()

    reopened = TaskStore(db)
    loaded = reopened.get(task.id)
    assert loaded is not None
    assert loaded.title == "Back up notes"
    assert loaded.status is TaskStatus.SUCCEEDED
    assert loaded.result == {"files": 3}
    assert loaded.metadata == {"source": "jarvis"}
    reopened.close()


def test_task_store_rejects_invalid_status(tmp_path):
    store = TaskStore(tmp_path / "tasks.db")
    task = store.create("Test")

    with pytest.raises(ValueError, match="invalid task status"):
        store.update(task.id, status="not-a-status")

    store.close()
