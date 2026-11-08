"""Bounded, read-only workspace intelligence for coding tasks."""

from __future__ import annotations

from pathlib import Path


class WorkspaceInspector:
    """Collect safe repository context without reading secrets or large files."""

    _SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache"}

    def __init__(self, root: Path, *, max_files: int = 200) -> None:
        self.root = root.resolve()
        self.max_files = max(1, max_files)

    def inspect(self) -> dict[str, object]:
        files: list[str] = []
        test_files = 0
        total = 0
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or any(part in self._SKIP for part in path.parts):
                continue
            relative = path.relative_to(self.root).as_posix()
            total += 1
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                test_files += 1
            if len(files) < self.max_files:
                files.append(relative)
        return {
            "root": str(self.root),
            "is_git_repo": (self.root / ".git").exists(),
            "file_count": total,
            "files": files,
            "test_files": test_files,
            "truncated": total > len(files),
        }


__all__ = ["WorkspaceInspector"]
