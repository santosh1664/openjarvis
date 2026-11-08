from openjarvis.personal.proactive import ProactiveAssistant
from openjarvis.personal.tasks import TaskStatus, TaskStore


def test_proactive_assistant_suggests_local_next_actions(tmp_path):
    store = TaskStore(tmp_path / "personal_tasks.db")
    task = store.create("Review release notes")
    store.update(task.id, status=TaskStatus.FAILED)
    store.create("Prepare demo")
    store.close()

    suggestions = ProactiveAssistant(tmp_path).suggestions()

    assert "Review pending task: Prepare demo" in suggestions
    assert "Retry or inspect failed task: Review release notes" in suggestions
