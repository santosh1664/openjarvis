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
        backend = self._session.get_tts_backend()
        if backend is None:
            return False
        voice_id, speed = self._session.voice_for_backend(backend)
        kwargs: dict[str, Any] = {"output_format": "wav", "speed": speed}
        if voice_id:
            kwargs["voice_id"] = voice_id
        result = backend.synthesize(text, **kwargs)
        if not result.audio:
            return False
        play_wav(result.audio, sample_rate=result.sample_rate)
        return True


__all__ = ["PersonalVoiceService"]
