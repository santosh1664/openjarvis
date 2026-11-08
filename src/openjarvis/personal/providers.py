"""Provider availability and fallback ordering for automatic model routing."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from typing import Any


class ProviderRouter:
    """Select configured providers without exposing API keys."""

    _PROVIDERS = (
        ("openrouter", "OPENROUTER_API_KEY"),
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("nvidia", "NVIDIA_API_KEY", "NIM_API_KEY"),
        ("huggingface", "HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN"),
        ("openai", "OPENAI_API_KEY"),
    )

    def status(self) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = {}
        for provider, *env_vars in self._PROVIDERS:
            active = next((name for name in env_vars if os.environ.get(name)), None)
            result[provider] = {
                "configured": active is not None,
                "env_var": active or env_vars[0],
            }
        return result

    def available(self) -> list[str]:
        if os.environ.get("OPENJARVIS_LOCAL_ONLY", "").lower() in {"1", "true", "yes"}:
            return []
        return [name for name, info in self.status().items() if info["configured"]]

    @staticmethod
    def local_only() -> bool:
        return os.environ.get("OPENJARVIS_LOCAL_ONLY", "").lower() in {
            "1",
            "true",
            "yes",
        }

    def choose(self, preferred: str | None = None) -> str | None:
        available = self.available()
        if preferred in available:
            return preferred
        return available[0] if available else None

    def fallback_models(self, *, task: str = "chat") -> list[str]:
        """Return provider-qualified model candidates in fallback order."""
        candidates: list[str] = []
        for provider in self.available():
            if provider == "openrouter":
                candidates.append("openrouter/auto")
            elif provider == "anthropic":
                candidates.append("claude-sonnet-4-20250514")
            elif provider == "nvidia":
                candidates.append("nvidia/llama-3.3-nemotron-super-49b-v1")
            elif provider == "huggingface":
                candidates.append("huggingface/auto")
            elif provider == "openai":
                candidates.append("gpt-4o-mini" if task == "chat" else "gpt-4o")
        return candidates

    @staticmethod
    def with_fallback(invoke: Callable[[str], Any], models: Sequence[str]) -> Any:
        """Invoke candidates in order and raise a summarized failure if all fail."""
        failures: list[str] = []
        for model in models:
            try:
                return invoke(model)
            except Exception as exc:
                failures.append(f"{model}: {exc}")
        if not failures:
            raise ValueError("no provider models configured")
        raise RuntimeError("all providers failed: " + "; ".join(failures))


__all__ = ["ProviderRouter"]
