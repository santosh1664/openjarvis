from __future__ import annotations

from openjarvis.memory.store import LocalFactStore
from openjarvis.personal.memory import PersonalMemory


def test_personal_memory_persists_preferences_and_reloads(tmp_path):
    path = tmp_path / "facts.jsonl"
    memory = PersonalMemory(LocalFactStore(path))

    assert memory.remember("response_style", "concise")
    assert memory.get("response_style") == "concise"

    reloaded = PersonalMemory(LocalFactStore(path))
    assert reloaded.get("response_style") == "concise"


def test_personal_memory_does_not_store_empty_preferences(tmp_path):
    memory = PersonalMemory(LocalFactStore(tmp_path / "facts.jsonl"))

    assert not memory.remember("", "value")
    assert not memory.remember("key", "")
