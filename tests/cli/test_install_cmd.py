from click.testing import CliRunner

from openjarvis.cli.install_cmd import install


def test_install_bootstraps_everything_in_one_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("openjarvis.cli.install_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.detect_hardware", lambda: object())
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_engine", lambda _: "local")
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_model", lambda *_: "model")
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.generate_default_toml", lambda *_args, **_kwargs: ""
    )

    result = CliRunner().invoke(install, ["--local-only"])

    assert result.exit_code == 0, result.output
    assert "Master install complete" in result.output
    assert (tmp_path / "personal_tasks.db").exists()
    assert (tmp_path / ".env.openjarvis.example").exists()


def test_install_can_skip_frontend_for_headless_setup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("openjarvis.cli.install_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("openjarvis.cli.setup_cmd.detect_hardware", lambda: object())
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_engine", lambda _: "local")
    monkeypatch.setattr("openjarvis.cli.setup_cmd.recommend_model", lambda *_: "model")
    monkeypatch.setattr(
        "openjarvis.cli.setup_cmd.generate_default_toml", lambda *_args, **_kwargs: ""
    )

    result = CliRunner().invoke(install, ["--no-frontend"])

    assert result.exit_code == 0, result.output
    assert "Frontend: skipped" in result.output
