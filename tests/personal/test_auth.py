from __future__ import annotations

from openjarvis.personal.auth import PasscodeStore


def test_passcode_is_hashed_and_verifies(tmp_path):
    store = PasscodeStore(tmp_path / "security.db")

    store.set_passcode("4829")

    assert store.is_configured()
    assert store.verify("4829")
    assert not store.verify("1234")
    assert "4829" not in (tmp_path / "security.db").read_bytes().decode(
        "utf-8", errors="ignore"
    )
    store.close()


def test_repeated_failures_lock_access_temporarily(tmp_path):
    store = PasscodeStore(tmp_path / "security.db", max_failures=2, lock_seconds=60)
    store.set_passcode("4829")

    assert not store.verify("wrong")
    assert not store.verify("wrong")
    assert not store.verify("4829")
    store.close()
