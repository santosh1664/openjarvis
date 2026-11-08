import json

from openjarvis.personal.sync import OfflineSyncStore


def test_offline_sync_round_trips_events_and_deduplicates(tmp_path):
    first = OfflineSyncStore(tmp_path / "one.db", device_id="one")
    event_id = first.record("memory", {"key": "tone", "value": "concise"})
    bundle = first.export_bundle()
    first.close()

    second = OfflineSyncStore(tmp_path / "two.db", device_id="two")
    assert second.import_bundle(bundle) == 1
    assert second.import_bundle(bundle) == 0
    assert second.pending() == [
        {
            "id": event_id,
            "kind": "memory",
            "payload": {"key": "tone", "value": "concise"},
        }
    ]
    second.close()


def test_sync_bundle_is_json_and_contains_no_device_secret(tmp_path):
    store = OfflineSyncStore(tmp_path / "sync.db", device_id="laptop")
    bundle = store.export_bundle()
    parsed = json.loads(bundle)
    assert parsed["version"] == 1
    assert parsed["device_id"] == "laptop"
    assert "secret" not in bundle
    store.close()
