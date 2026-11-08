from __future__ import annotations

from openjarvis.personal.providers import ProviderRouter


def test_provider_router_orders_configured_providers(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    monkeypatch.setenv("NVIDIA_API_KEY", "secret")
    monkeypatch.delenv("HF_TOKEN", raising=False)

    router = ProviderRouter()

    assert router.available()[:3] == ["openrouter", "anthropic", "nvidia"]
    assert router.choose() == "openrouter"


def test_provider_router_never_returns_secret_values(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")

    status = ProviderRouter().status()

    assert status["openrouter"] == {"configured": True, "env_var": "OPENROUTER_API_KEY"}
    assert "secret" not in repr(status)
