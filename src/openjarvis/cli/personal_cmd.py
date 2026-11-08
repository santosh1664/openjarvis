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
    ProviderRouter,
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


@personal.group("provider")
def provider() -> None:
    """Inspect configured inference providers."""


@provider.command("status")
def provider_status() -> None:
    """Show provider availability without displaying secrets."""
    router = ProviderRouter()
    for name, info in router.status().items():
        state = "configured" if info["configured"] else "not configured"
        Console().print(f"- {name}: {state} ({info['env_var']})")
    Console().print(f"Preferred provider: {router.choose() or 'local-only'}")
    fallback = router.fallback_models()
    if fallback:
        Console().print("Fallback models: " + " -> ".join(fallback))


@personal.command("status")
def status() -> None:
    """Show a local dashboard summary for the personal JARVIS runtime."""
    config_dir = get_config_dir()
    profiles = ProfileStore(config_dir / "profiles.db")
    automation = PersonalAutomation(config_dir / "scheduler.db")
    passcode = PasscodeStore(config_dir / "security.db")
    try:
        profile_count = len(profiles.list())
        automation_count = len(automation.list(status="active"))
        passcode_state = "configured" if passcode.is_configured() else "not configured"
    finally:
        profiles.close()
        automation.close()
        passcode.close()
    providers = ProviderRouter()
    console = Console()
    console.print("[bold]JARVIS Personal Status[/bold]")
    console.print(f"Profiles: {profile_count}/3")
    console.print(f"Active automations: {automation_count}")
    console.print(f"Passcode: {passcode_state}")
    console.print(f"Providers: {', '.join(providers.available()) or 'local-only'}")


@personal.command("approvals")
def approvals() -> None:
    """List pending sensitive actions awaiting approval."""
    from openjarvis.tools.approval_store import ApprovalStore

    store = ApprovalStore(get_config_dir() / "approvals.db")
    try:
        pending = store.list_pending()
    finally:
        store.close()
    console = Console()
    if not pending:
        console.print("[dim]No pending approvals.[/dim]")
        return
    console.print("[bold]Pending approvals[/bold]")
    for action in pending:
        console.print(
            f"- {action.id}: {action.description} "
            f"({action.action_type}, tier={action.tier})"
        )


__all__ = ["personal"]
