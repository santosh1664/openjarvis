"""``jarvis personal`` — personal JARVIS memory and automation commands."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from openjarvis.core.paths import get_config_dir
from openjarvis.memory.store import LocalFactStore
from openjarvis.personal import (
    OfflineSyncStore,
    PasscodeStore,
    PersonalAutomation,
    PersonalDiagnostics,
    PersonalKnowledgeGraph,
    PersonalMemory,
    ProfileStore,
    ProviderRouter,
    WorkspaceInspector,
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


@personal.command("privacy")
def privacy() -> None:
    """Show provider/data-boundary privacy information without secrets."""
    router = ProviderRouter()
    configured = router.available()
    console = Console()
    console.print("[bold]JARVIS Privacy Center[/bold]")
    console.print("Local processing: available")
    if configured:
        console.print("Cloud providers configured: " + ", ".join(configured))
        console.print(
            "Cloud use: possible; requests remain subject to the active "
            "security policy."
        )
    else:
        console.print("Cloud providers configured: none")
        console.print("Cloud use: disabled by availability")
    console.print("API keys: hidden")


@personal.group("knowledge")
def knowledge() -> None:
    """Manage the local personal knowledge graph."""


@knowledge.command("add")
@click.argument("kind")
@click.argument("name")
@click.argument("description", required=False, default="")
def knowledge_add(kind: str, name: str, description: str) -> None:
    graph = PersonalKnowledgeGraph(get_config_dir() / "knowledge.db")
    try:
        graph.upsert_entity(kind, name, description)
    finally:
        graph.close()
    click.echo(f"Added knowledge entity: {name}")


@knowledge.command("link")
@click.argument("source")
@click.argument("predicate")
@click.argument("target")
def knowledge_link(source: str, predicate: str, target: str) -> None:
    graph = PersonalKnowledgeGraph(get_config_dir() / "knowledge.db")
    try:
        graph.link(source, predicate, target)
    finally:
        graph.close()
    click.echo(f"Linked {source} --{predicate}--> {target}")


@knowledge.command("find")
@click.argument("text")
def knowledge_find(text: str) -> None:
    graph = PersonalKnowledgeGraph(get_config_dir() / "knowledge.db")
    try:
        entities = graph.find(text)
        links = [
            link for entity in entities for link in graph.links_touching(entity["name"])
        ]
    finally:
        graph.close()
    for entity in entities:
        click.echo(f"{entity['name']} ({entity['kind']}): {entity['description']}")
    for source, predicate, target in links:
        click.echo(f"{source} --{predicate}--> {target}")


@personal.command("diagnostics")
@click.option("--repair", is_flag=True, help="Repair safe missing local state.")
def diagnostics(repair: bool) -> None:
    """Check and optionally repair local JARVIS state."""
    report = PersonalDiagnostics(get_config_dir()).run(repair=repair)
    click.echo("JARVIS Diagnostics")
    click.echo(f"Config directory: {report['config_dir']}")
    click.echo(f"Config permissions: {report['config_permissions']}")
    providers = report["providers"]
    configured = [name for name, active in providers.items() if active]
    click.echo("Configured providers: " + (", ".join(configured) or "none"))
    click.echo("Repaired: " + (", ".join(report["repaired"]) or "none"))


@personal.group("sync")
def sync() -> None:
    """Exchange user-controlled offline sync bundles."""


@sync.command("export")
@click.option("--device-id", required=True)
@click.argument("output", type=click.Path(dir_okay=False, writable=True))
def sync_export(device_id: str, output: str) -> None:
    store = OfflineSyncStore(get_config_dir() / "sync.db", device_id=device_id)
    try:
        bundle = store.export_bundle()
    finally:
        store.close()
    with open(output, "w", encoding="utf-8") as handle:
        handle.write(bundle)
    click.echo(f"Exported offline bundle to {output}")


@sync.command("import")
@click.argument("bundle", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--device-id", required=True)
def sync_import(bundle: str, device_id: str) -> None:
    with open(bundle, encoding="utf-8") as handle:
        content = handle.read()
    store = OfflineSyncStore(get_config_dir() / "sync.db", device_id=device_id)
    try:
        added = store.import_bundle(content)
    finally:
        store.close()
    click.echo(f"Imported {added} new offline events")


@personal.command("workspace")
@click.argument("root", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("--max-files", default=50, show_default=True)
def workspace(root: str, max_files: int) -> None:
    """Inspect a coding workspace without modifying it."""
    report = WorkspaceInspector(Path(root), max_files=max_files).inspect()
    click.echo("JARVIS Workspace Intelligence")
    click.echo(f"Root: {report['root']}")
    click.echo(f"Git repository: {'yes' if report['is_git_repo'] else 'no'}")
    click.echo(f"Files: {report['file_count']} ({report['test_files']} test files)")
    if report["truncated"]:
        click.echo(f"Showing first {len(report['files'])} files")
    for filename in report["files"]:
        click.echo(f"- {filename}")


__all__ = ["personal"]
