from openjarvis.engine.multi import MultiEngine


class FakeEngine:
    def __init__(self, models, failures=()):
        self.models = models
        self.failures = set(failures)
        self.calls = []

    def list_models(self):
        return self.models

    def generate(self, messages, *, model, **kwargs):
        self.calls.append(model)
        if model in self.failures:
            raise RuntimeError(f"{model} unavailable")
        return {"content": model}

    def health(self):
        return True

    def close(self):
        pass


def test_cloud_generation_fails_over_to_configured_provider(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "configured")
    cloud = FakeEngine(
        ["claude-sonnet-4-20250514", "openrouter/auto"],
        failures={"claude-sonnet-4-20250514"},
    )
    engine = MultiEngine([("cloud", cloud)])

    result = engine.generate([], model="claude-sonnet-4-20250514")

    assert result["content"] == "openrouter/auto"
    assert cloud.calls == ["claude-sonnet-4-20250514", "openrouter/auto"]


def test_failover_does_not_switch_local_models(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "configured")
    local = FakeEngine(["local-model"], failures={"local-model"})
    engine = MultiEngine([("local", local)])

    try:
        engine.generate([], model="local-model")
    except RuntimeError as exc:
        assert "unavailable" in str(exc)
    else:
        raise AssertionError("local failure unexpectedly succeeded")
    assert local.calls == ["local-model"]
