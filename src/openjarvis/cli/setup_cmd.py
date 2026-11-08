"""``jarvis setup`` — initialize the personal JARVIS foundation."""

from __future__ import annotations

import click
import httpx
from rich.console import Console

from openjarvis.core.config import (
    detect_hardware,
    generate_default_toml,
    recommend_engine,
    recommend_model,
)
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
    hardware = detect_hardware()
    engine = recommend_engine(hardware)
    model = recommend_model(hardware, engine)
    config_path = config_dir / "config.toml"
    if not config_path.exists():
        config_path.write_text(
            generate_default_toml(hardware, engine=engine), encoding="utf-8"
        )
    task_store = TaskStore(config_dir / "personal_tasks.db")
    task_store.close()
    audit_log = PermissionAuditLog(config_dir / "permission_audit.db")
    audit_log.close()
    Console().print("[green]JARVIS setup complete.[/green]")
    Console().print(f"  State directory: {config_dir}")
    Console().print(f"  Inference engine: {engine}")
    Console().print(f"  Recommended model: {model or 'manual selection required'}")
    if engine == "ollama" and model:
        try:
            probe = httpx.get("http://localhost:11434/api/tags", timeout=1.0)
            if probe.status_code < 500:
                from openjarvis.cli.model import ollama_pull

                if ollama_pull("http://localhost:11434", model, Console()):
                    Console().print("  Model: ready")
                else:
                    Console().print("  Model: pull failed; run `jarvis doctor`")
            else:
                Console().print("  Model: Ollama is not ready; run `ollama serve`")
        except Exception:
            Console().print("  Model: Ollama is not running; setup will resume later")
    Console().print("  Permissions: deny-by-default")
    Console().print("  Autonomous execution: bounded")


__all__ = ["setup"]
