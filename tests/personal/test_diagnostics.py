from openjarvis.personal.diagnostics import PersonalDiagnostics


def test_diagnostics_repairs_missing_config_dir(tmp_path):
    config = tmp_path / "nested" / "config"
    report = PersonalDiagnostics(config).run(repair=True)

    assert config.is_dir()
    assert report["config_dir"] == "ready"
    assert report["repaired"] == ["config_dir"]


def test_diagnostics_never_reports_secret_values(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "super-secret")
    report = PersonalDiagnostics(tmp_path).run()

    rendered = repr(report)
    assert "super-secret" not in rendered
    assert report["providers"]["openrouter"] is True
