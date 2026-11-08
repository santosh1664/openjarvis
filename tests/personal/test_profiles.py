from __future__ import annotations

import pytest

from openjarvis.personal.profiles import ProfileStore


def test_profile_store_supports_three_separate_conversations(tmp_path):
    store = ProfileStore(tmp_path / "profiles.db")
    alice = store.create("Alice")
    bob = store.create("Bob")
    store.create("Carol")

    store.add_message(alice.id, "user", "I like Telugu music")
    store.add_message(bob.id, "user", "I prefer English")

    assert [m.content for m in store.messages(alice.id)] == ["I like Telugu music"]
    assert [m.content for m in store.messages(bob.id)] == ["I prefer English"]


def test_profile_store_rejects_a_fourth_profile_and_routes_name(tmp_path):
    store = ProfileStore(tmp_path / "profiles.db")
    for name in ("Alice", "Bob", "Carol"):
        store.create(name)

    with pytest.raises(ValueError, match="maximum of 3"):
        store.create("Dave")

    assert store.match_address("Alice, remember this") == "Alice"
    assert store.match_address("hello jarvis") is None
    profile, content = store.route("Alice, remember this")
    assert profile is not None and profile.name == "Alice"
    assert content == "remember this"
