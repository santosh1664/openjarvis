from click.testing import CliRunner

from openjarvis.cli.setup_cmd import setup


def test_full_setup_initializes_personal_state(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(setup, ["--full"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "personal_tasks.db").exists()
    assert (tmp_path / "permission_audit.db").exists()
    assert "JARVIS setup complete" in result.output


def test_full_setup_generates_config_and_reports_model(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.detect_hardware", lambda: object())
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_engine", lambda _: "ollama")
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.recommend_model", lambda *_: "qwen3.5:4b"
    )
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.generate_default_toml",
        lambda *_args, **_kwargs: '[engine]\ndefault = "ollama"\n',
    )

    result = CliRunner().invoke(setup, ["--full"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "config.toml").read_text() == '[engine]\ndefault = "ollama"\n'
    assert "qwen3.5:4b" in result.output


def test_full_setup_can_start_voice_chat(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.detect_hardware", lambda: object())
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_engine", lambda _: "ollama")
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_model", lambda *_: "model")
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.generate_default_toml", lambda *_args, **_kwargs: ""
    )
    called = []
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.launch_chat",
        lambda voice: called.append(voice),
    )

    result = CliRunner().invoke(setup, ["--full", "--start", "--voice"])

    assert result.exit_code == 0, result.output
    assert called == [True]
