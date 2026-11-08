from __future__ import annotations

from openjarvis.personal.coding import AutonomousCodingService


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def run_ephemeral(self, agent_type, system_prompt, input_text, tools):
        self.calls.append((agent_type, system_prompt, input_text, tools))
        return {"content": "implemented", "agent_type": agent_type}


def test_coding_service_runs_through_bounded_personal_task(tmp_path):
    executor = FakeExecutor()
    service = AutonomousCodingService(tmp_path / "jarvis.db", executor)

    task_id, result = service.run("Add a test", workspace=str(tmp_path))

    assert task_id
    assert result["content"] == "implemented"
    assert executor.calls[0][0] == "native_openhands"
    assert "file_read" in executor.calls[0][3]
    assert service.get_task(task_id).status.value == "succeeded"
