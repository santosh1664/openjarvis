"""Personal voice interaction using OpenJarvis's existing speech backends."""

from __future__ import annotations

from typing import Any

from openjarvis.speech.voice_io import play_wav


class PersonalVoiceService:
    def __init__(self, session: Any) -> None:
        self._session = session

    def speak(self, text: str) -> bool:
        if not text.strip():
            return False
        for _attempt in range(2):
            backend = self._session.get_tts_backend()
            if backend is None:
                return False
            try:
                voice_id, speed = self._session.voice_for_backend(backend)
                kwargs: dict[str, Any] = {"output_format": "wav", "speed": speed}
                if voice_id:
                    kwargs["voice_id"] = voice_id
                result = backend.synthesize(text, **kwargs)
                if not result.audio:
                    return False
                play_wav(result.audio, sample_rate=result.sample_rate)
                return True
            except Exception:
                discard = getattr(self._session, "discard_tts_backend", None)
                if callable(discard):
                    discard()
        return False

    def detected_language(self) -> str | None:
        """Return the last detected input language for reply routing."""
        return getattr(self._session, "last_detected_language", None)


__all__ = ["PersonalVoiceService"]
