"""Provider availability and fallback ordering for automatic model routing."""

from __future__ import annotations

import os


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
        return [name for name, info in self.status().items() if info["configured"]]

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


__all__ = ["ProviderRouter"]
