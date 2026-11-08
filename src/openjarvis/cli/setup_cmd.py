"""``jarvis setup`` — initialize the personal JARVIS foundation."""

from __future__ import annotations

import click
from rich.console import Console

from openjarvis.core.paths import get_config_dir
from openjarvis.personal import PermissionAuditLog, TaskStore


@click.command("setup")
@click.option("--full", is_flag=True, help="Initialize all local JARVIS state.")
def setup(full: bool) -> None:
    """Initialize local state for personal JARVIS features."""
    if not full:
        raise click.UsageError("use `jarvis setup --full` to initialize JARVIS")
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    task_store = TaskStore(config_dir / "personal_tasks.db")
    task_store.close()
    audit_log = PermissionAuditLog(config_dir / "permission_audit.db")
    audit_log.close()
    Console().print("[green]JARVIS setup complete.[/green]")
    Console().print(f"  State directory: {config_dir}")
    Console().print("  Permissions: deny-by-default")
    Console().print("  Autonomous execution: bounded")


__all__ = ["setup"]
