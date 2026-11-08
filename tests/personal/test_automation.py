from __future__ import annotations

import pytest

from openjarvis.personal.automation import PersonalAutomation


def test_personal_automation_persists_restartable_schedule(tmp_path):
    automation = PersonalAutomation(tmp_path / "scheduler.db")

    task = automation.create(
        "Check inbox", schedule_type="interval", schedule_value="60"
    )

    assert task["status"] == "active"
    assert task["agent"] == "operative"
    automation.close()
    reopened = PersonalAutomation(tmp_path / "scheduler.db")
    assert reopened.list()[0]["prompt"] == "Check inbox"
    reopened.close()


def test_personal_automation_rejects_unsafe_schedule(tmp_path):
    automation = PersonalAutomation(tmp_path / "scheduler.db")

    with pytest.raises(ValueError, match="schedule"):
        automation.create("Bad", schedule_type="interval", schedule_value="0")

    automation.close()
