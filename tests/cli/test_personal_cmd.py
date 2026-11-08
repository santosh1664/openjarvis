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


def test_personal_profile_create_and_list(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)

    created = CliRunner().invoke(personal, ["profile", "create", "Alice"])
    listed = CliRunner().invoke(personal, ["profile", "list"])

    assert created.exit_code == 0, created.output
    assert listed.exit_code == 0, listed.output
    assert "Alice" in listed.output
