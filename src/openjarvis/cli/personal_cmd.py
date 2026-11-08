"""``jarvis personal`` — personal JARVIS memory and automation commands."""

from __future__ import annotations

import click
from rich.console import Console

from openjarvis.core.paths import get_config_dir
from openjarvis.memory.store import LocalFactStore
from openjarvis.personal import PersonalAutomation, PersonalMemory


@click.group("personal")
def personal() -> None:
    """Manage personal JARVIS preferences and automations."""


@personal.command("remember")
@click.argument("key")
@click.argument("value")
def remember(key: str, value: str) -> None:
    """Remember a durable user preference."""
    store = LocalFactStore(get_config_dir() / "memory_facts.jsonl")
    if not PersonalMemory(store).remember(key, value):
        raise click.ClickException("Preference key and value must not be empty")
    Console().print(f"[green]Remembered {key}.[/green]")


@personal.command("automate")
@click.argument("prompt")
@click.option(
    "--type",
    "schedule_type",
    required=True,
    type=click.Choice(["cron", "interval", "once"]),
)
@click.option("--value", "schedule_value", required=True)
@click.option("--agent", default="operative")
@click.option("--tools", default="")
def automate(
    prompt: str, schedule_type: str, schedule_value: str, agent: str, tools: str
) -> None:
    """Create a durable automation executed by the scheduler."""
    automation = PersonalAutomation(get_config_dir() / "scheduler.db")
    try:
        task = automation.create(
            prompt,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            agent=agent,
            tools=tools,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        automation.close()
    Console().print(f"[green]Created automation {task['id']}.[/green]")


__all__ = ["personal"]
