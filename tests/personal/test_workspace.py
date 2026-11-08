from openjarvis.personal.workspace import WorkspaceInspector


def test_workspace_inspector_reports_repo_context(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("# demo\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_demo.py").write_text(
        "def test_ok(): pass\n", encoding="utf-8"
    )

    report = WorkspaceInspector(tmp_path).inspect()

    assert report["is_git_repo"] is True
    assert report["file_count"] == 2
    assert "README.md" in report["files"]
    assert report["test_files"] == 1


def test_workspace_inspector_is_bounded(tmp_path):
    for index in range(20):
        (tmp_path / f"file-{index}.txt").write_text("x", encoding="utf-8")

    report = WorkspaceInspector(tmp_path, max_files=5).inspect()

    assert report["file_count"] == 20
    assert len(report["files"]) == 5
    assert report["truncated"] is True
