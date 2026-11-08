"""``jarvis personal`` — personal JARVIS memory and automation commands."""

from __future__ import annotations

import click
from rich.console import Console

from openjarvis.core.paths import get_config_dir
from openjarvis.memory.store import LocalFactStore
from openjarvis.personal import (
    PasscodeStore,
    PersonalAutomation,
    PersonalMemory,
    ProfileStore,
)


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


@personal.group("profile")
def profile() -> None:
    """Manage the three isolated JARVIS profiles."""


@profile.command("create")
@click.argument("name")
def profile_create(name: str) -> None:
    """Create a named profile."""
    store = ProfileStore(get_config_dir() / "profiles.db")
    try:
        created = store.create(name)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        store.close()
    Console().print(f"[green]Created profile {created.name}.[/green]")


@profile.command("list")
def profile_list() -> None:
    """List configured profiles."""
    store = ProfileStore(get_config_dir() / "profiles.db")
    try:
        profiles = store.list()
    finally:
        store.close()
    if not profiles:
        Console().print("[dim]No profiles configured.[/dim]")
        return
    for item in profiles:
        Console().print(f"- {item.name}")


@personal.group("security")
def security() -> None:
    """Manage the JARVIS security passcode."""


@security.command("set-passcode")
def set_passcode() -> None:
    """Set or replace the local passcode used for sensitive actions."""
    first = click.prompt("Passcode", hide_input=True, confirmation_prompt=False)
    second = click.prompt("Repeat passcode", hide_input=True, confirmation_prompt=False)
    if first != second:
        raise click.ClickException("Passcodes do not match")
    store = PasscodeStore(get_config_dir() / "security.db")
    try:
        store.set_passcode(first)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        store.close()
    Console().print(
        "[green]Passcode enabled. Sensitive actions require verification.[/green]"
    )


__all__ = ["personal"]
