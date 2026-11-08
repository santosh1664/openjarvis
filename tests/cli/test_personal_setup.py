from click.testing import CliRunner

from openjarvis.cli.setup_cmd import setup


def test_full_setup_initializes_personal_state(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(setup, ["--full"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "personal_tasks.db").exists()
    assert (tmp_path / "permission_audit.db").exists()
    assert "JARVIS setup complete" in result.output
