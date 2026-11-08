from __future__ import annotations

from openjarvis.personal.voice import PersonalVoiceService


class FakeSession:
    def __init__(self):
        self.spoken = []

    def get_tts_backend(self):
        return object()

    def voice_for_backend(self, backend):
        return "voice", 1.0


def test_personal_voice_service_uses_existing_voice_session(tmp_path, monkeypatch):
    session = FakeSession()
    played = []
    monkeypatch.setattr(
        "openjarvis.personal.voice.play_wav",
        lambda audio, sample_rate: played.append((audio, sample_rate)),
    )
    session.get_tts_backend = lambda: type(
        "Backend",
        (),
        {
            "synthesize": lambda *_args, **_kwargs: type(
                "Audio", (), {"audio": b"reply", "sample_rate": 24000}
            )()
        },
    )()
    service = PersonalVoiceService(session)

    assert service.speak("Hello") is True
    assert played == [(b"reply", 24000)]


def test_personal_voice_service_discards_failed_backend_and_retries(monkeypatch):
    played = []

    class Session(FakeSession):
        def __init__(self):
            self.backends = [
                type(
                    "Bad",
                    (),
                    {
                        "synthesize": lambda *_a, **_k: (_ for _ in ()).throw(
                            RuntimeError()
                        )
                    },
                )(),
                type(
                    "Good",
                    (),
                    {
                        "synthesize": lambda *_a, **_k: type(
                            "Audio", (), {"audio": b"ok", "sample_rate": 1}
                        )()
                    },
                )(),
            ]

        def get_tts_backend(self):
            return self.backends[0] if self.backends else None

        def discard_tts_backend(self):
            self.backends.pop(0)

    monkeypatch.setattr(
        "openjarvis.personal.voice.play_wav", lambda a, sample_rate: played.append(a)
    )
    assert PersonalVoiceService(Session()).speak("hello") is True
    assert played == [b"ok"]
