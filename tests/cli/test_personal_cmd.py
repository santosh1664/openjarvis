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


def test_personal_security_set_passcode(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(
        personal,
        ["security", "set-passcode"],
        input="4829\n4829\n",
    )

    assert result.exit_code == 0, result.output
    assert "Passcode enabled" in result.output


def test_personal_provider_status_redacts_keys(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-value")

    result = CliRunner().invoke(personal, ["provider", "status"])

    assert result.exit_code == 0, result.output
    assert "openrouter: configured" in result.output
    assert "secret-value" not in result.output


def test_personal_status_summarizes_local_state(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)

    result = CliRunner().invoke(personal, ["status"])

    assert result.exit_code == 0, result.output
    assert "JARVIS Personal Status" in result.output
    assert "Profiles: 0/3" in result.output
    assert "Passcode: not configured" in result.output


def test_personal_approvals_lists_pending_actions(tmp_path, monkeypatch):
    monkeypatch.setattr("openjarvis.cli.personal_cmd.get_config_dir", lambda: tmp_path)
    from openjarvis.tools.approval_store import ApprovalStore

    store = ApprovalStore(tmp_path / "approvals.db")
    store.queue_action("file_write", "Write report", {}, "file:write", "medium")

    result = CliRunner().invoke(personal, ["approvals"])

    assert result.exit_code == 0, result.output
    assert "Write report" in result.output
    store.close()


def test_personal_privacy_reports_cloud_boundary(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")

    result = CliRunner().invoke(personal, ["privacy"])

    assert result.exit_code == 0, result.output
    assert "Privacy Center" in result.output
    assert "anthropic" in result.output
    assert "secret" not in result.output
