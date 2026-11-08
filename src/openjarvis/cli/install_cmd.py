"""One-command local installation and personal JARVIS bootstrap."""

from __future__ import annotations

import os

import click
from rich.console import Console

from openjarvis.cli.setup_cmd import setup
from openjarvis.core.paths import get_config_dir
from openjarvis.personal import PersonalDiagnostics


@click.command("install")
@click.option("--start", is_flag=True, help="Start text chat after installation.")
@click.option("--voice", is_flag=True, help="Start voice chat after installation.")
@click.option("--local-only", is_flag=True, help="Disable all cloud providers.")
def install(start: bool, voice: bool, local_only: bool) -> None:
    """Install dependencies separately, then initialize all local JARVIS state."""
    previous_local_only = os.environ.get("OPENJARVIS_LOCAL_ONLY")
    if local_only:
        os.environ["OPENJARVIS_LOCAL_ONLY"] = "1"
    try:
        setup.callback(full=True, start=False, voice=False)
    finally:
        if local_only and not (start or voice):
            if previous_local_only is None:
                os.environ.pop("OPENJARVIS_LOCAL_ONLY", None)
            else:
                os.environ["OPENJARVIS_LOCAL_ONLY"] = previous_local_only
    config_dir = get_config_dir()
    template = config_dir / ".env.openjarvis.example"
    if not template.exists():
        template.write_text(
            "# Secret-free provider template; set values in your shell.\n"
            "OPENROUTER_API_KEY=\nANTHROPIC_API_KEY=\nNVIDIA_API_KEY=\n"
            "NIM_API_KEY=\nHF_TOKEN=\nOPENAI_API_KEY=\n",
            encoding="utf-8",
        )
    report = PersonalDiagnostics(config_dir).run(repair=True)
    Console().print(f"[green]Master install complete.[/green] State: {config_dir}")
    Console().print(f"Provider template: {template}")
    Console().print(f"Diagnostics: {report['config_dir']}")
    if start or voice:
        from openjarvis.cli.chat_cmd import chat

        chat.main(args=["--voice"] if voice else [], standalone_mode=False)


__all__ = ["install"]
