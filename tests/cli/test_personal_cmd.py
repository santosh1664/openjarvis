from click.testing import CliRunner

from openjarvis.cli.personal_cmd import personal


def test_personal_remember_persists_preference(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(personal, ["remember", "style", "concise"])

    assert result.exit_code == 0, result.output
    assert "Remembered" in result.output


def test_personal_automate_creates_schedule(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(
        personal,
        ["automate", "Check inbox", "--type", "interval", "--value", "60"],
    )

    assert result.exit_code == 0, result.output
    assert "Created automation" in result.output
