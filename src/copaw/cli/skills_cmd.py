# -*- coding: utf-8 -*-
"""CLI skill: list and interactively enable/disable skills."""
from __future__ import annotations

import json
import click
from pathlib import Path
from rich.table import Table
from rich.console import Console

from ..agents.skills_manager import SkillService, list_available_skills
from ..agents.skills_hub import search_hub_skills, install_skill_from_hub
from .utils import prompt_checkbox, prompt_confirm, prompt_text, prompt_select

console = Console()


# pylint: disable=too-many-branches
def configure_skills_interactive() -> None:
    """Interactively select which skills to enable (multi-select)."""
    all_skills = SkillService.list_all_skills()
    if not all_skills:
        click.echo("No skills found. Nothing to configure.")
        return

    available = set(list_available_skills())
    all_names = {s.name for s in all_skills}

    # Default to all skills if nothing is currently active (first time)
    default_checked = available if available else all_names

    # Build checkbox options: (label, value)
    options: list[tuple[str, str]] = []
    for skill in sorted(all_skills, key=lambda s: s.name):
        status = "✓" if skill.name in available else "✗"
        label = f"{skill.name}  [{status}] ({skill.source})"
        options.append((label, skill.name))

    click.echo("\n=== Skills Configuration ===")
    click.echo("Use ↑/↓ to move, <space> to toggle, <enter> to confirm.\n")

    selected = prompt_checkbox(
        "Select skills to enable:",
        options=options,
        checked=default_checked,
        select_all_option=False,
    )

    # Ctrl+C → cancel
    if selected is None:
        click.echo("\n\nOperation cancelled.")
        return

    selected_set = set(selected)

    # Show preview of changes
    to_enable = selected_set - available
    to_disable = (all_names & available) - selected_set

    if not to_enable and not to_disable:
        click.echo("\nNo changes needed.")
        return

    click.echo()
    if to_enable:
        click.echo(
            click.style(
                f"  + Enable:  {', '.join(sorted(to_enable))}",
                fg="green",
            ),
        )
    if to_disable:
        click.echo(
            click.style(
                f"  - Disable: {', '.join(sorted(to_disable))}",
                fg="red",
            ),
        )

    # Confirm save or skip
    save = prompt_confirm("Apply changes?", default=True)
    if not save:
        click.echo("Skipped. No changes applied.")
        return

    # Apply changes
    for name in to_enable:
        result = SkillService.enable_skill(name)
        if result:
            click.echo(f"  ✓ Enabled: {name}")
        else:
            click.echo(
                click.style(f"  ✗ Failed to enable: {name}", fg="red"),
            )

    for name in to_disable:
        result = SkillService.disable_skill(name)
        if result:
            click.echo(f"  ✓ Disabled: {name}")
        else:
            click.echo(
                click.style(f"  ✗ Failed to disable: {name}", fg="red"),
            )

    click.echo("\n✓ Skills configuration updated!")


@click.group("skills")
def skills_group() -> None:
    """Manage skills (list / configure)."""


@skills_group.command("list")
@click.option(
    "--enabled/--all",
    default=True,
    help="Show only enabled skills (default) or all skills",
)
@click.option(
    "--source",
    type=click.Choice(["builtin", "customized", "all"]),
    default="all",
    help="Filter by source",
)
def list_cmd(enabled: bool, source: str):
    """Show all skills and their enabled/disabled status."""
    all_skills = SkillService.list_all_skills()
    available = set(list_available_skills())
    
    # Filter skills
    skills = all_skills
    if source != "all":
        skills = [s for s in skills if s.source == source]
    
    if enabled:
        skills = [s for s in skills if s.name in available]
    
    if not skills:
        console.print("[yellow]No skills found.[/yellow]")
        return
    
    # Create table
    table = Table(title="Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Source", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Path", style="dim")
    
    for skill in sorted(skills, key=lambda s: s.name):
        status = "✓ Enabled" if skill.name in available else "✗ Disabled"
        table.add_row(
            skill.name,
            skill.source,
            status,
            str(skill.path),
        )
    
    console.print(table)
    console.print(f"\nTotal: {len(skills)} skill(s)")


@skills_group.command("config")
def configure_cmd() -> None:
    configure_skills_interactive()


@skills_group.command("info")
@click.argument("name")
def info_skill(name: str):
    """Show detailed information about a skill."""
    all_skills = SkillService.list_all_skills()
    available = set(list_available_skills())
    
    # Find skill
    skill = next((s for s in all_skills if s.name == name), None)
    
    if not skill:
        console.print(f"[red]Error: Skill '{name}' not found.[/red]")
        return
    
    is_enabled = skill.name in available
    
    console.print(f"\n[cyan]=== Skill: {skill.name} ===[/cyan]\n")
    console.print(f"[green]Name:[/green]       {skill.name}")
    console.print(f"[green]Source:[/green]      {skill.source}")
    console.print(f"[green]Status:[/green]      {'✓ Enabled' if is_enabled else '✗ Disabled'}")
    console.print(f"[green]Path:[/green]        {skill.path}")
    
    # Try to read description from SKILL.md
    skill_md = Path(skill.path) / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        # Extract description from frontmatter
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx > 0:
                frontmatter = content[4:end_idx].strip()
                for line in frontmatter.split("\n"):
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                        console.print(f"[green]Description:[/green] {desc}")
                        break
    
    console.print()


@skills_group.command("enable")
@click.argument("name")
def enable_skill(name: str):
    """Enable a skill."""
    result = SkillService.enable_skill(name)
    if result:
        console.print(f"[green]✓ Skill '{name}' enabled.[/green]")
    else:
        console.print(f"[red]✗ Failed to enable skill '{name}'.[/red]")


@skills_group.command("disable")
@click.argument("name")
def disable_skill(name: str):
    """Disable a skill."""
    result = SkillService.disable_skill(name)
    if result:
        console.print(f"[green]✓ Skill '{name}' disabled.[/green]")
    else:
        console.print(f"[red]✗ Failed to disable skill '{name}'.[/red]")


@skills_group.command("export")
@click.argument("output_file", type=click.Path())
@click.option("--enabled-only", is_flag=True, help="Export only enabled skills")
def export_skills(output_file: str, enabled_only: bool):
    """Export skills configuration to JSON file."""
    all_skills = SkillService.list_all_skills()
    available = set(list_available_skills())
    
    # Filter skills
    skills = all_skills
    if enabled_only:
        skills = [s for s in skills if s.name in available]
    
    if not skills:
        console.print("[yellow]No skills to export.[/yellow]")
        return
    
    # Export data
    export_data = {
        "skills": [
            {
                "name": skill.name,
                "source": skill.source,
                "enabled": skill.name in available,
            }
            for skill in skills
        ]
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓ Exported {len(skills)} skill(s) to {output_file}[/green]")


@skills_group.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--enable", is_flag=True, default=False, help="Enable skills after import")
def import_skills(input_file: str, enable: bool):
    """Import skills configuration from JSON file."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON file: {e}[/red]")
        return
    
    skills_data = data.get("skills", [])
    if not skills_data:
        console.print("[yellow]No skills found in file.[/yellow]")
        return
    
    all_skills = SkillService.list_all_skills()
    all_names = {s.name for s in all_skills}
    
    imported = 0
    skipped = 0
    
    for skill_data in skills_data:
        name = skill_data.get("name")
        if not name:
            continue
        
        if name not in all_names:
            console.print(f"[yellow]Skipping unknown skill: {name}[/yellow]")
            skipped += 1
            continue
        
        # Enable if requested
        if enable or skill_data.get("enabled", False):
            result = SkillService.enable_skill(name)
            if result:
                console.print(f"[green]✓ Enabled: {name}[/green]")
                imported += 1
    
    console.print(f"\n[green]✓ Imported {imported} skill(s), skipped {skipped}[/green]")


@skills_group.command("search")
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results")
def search_skills(query: str, limit: int):
    """Search for skills in the hub."""
    console.print(f"[cyan]Searching for '{query}'...[/cyan]\n")
    
    try:
        results = search_hub_skills(query, limit=limit)
        
        if not results:
            console.print("[yellow]No skills found.[/yellow]")
            return
        
        table = Table(title=f"Search Results: {query}")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="dim")
        table.add_column("Version", style="yellow")
        table.add_column("Source", style="green")
        
        for skill in results:
            table.add_row(
                skill.name,
                skill.description[:50] + "..." if len(skill.description) > 50 else skill.description,
                skill.version,
                skill.source_url,
            )
        
        console.print(table)
        console.print(f"\nTotal: {len(results)} result(s)")
        
    except Exception as e:
        console.print(f"[red]Error searching skills: {e}[/red]")


@skills_group.command("install")
@click.argument("url")
@click.option("--version", default="", help="Specific version to install")
@click.option("--enable/--no-enable", default=True, help="Enable skill after install")
@click.option("--overwrite", is_flag=True, help="Overwrite existing skill")
def install_skill(url: str, version: str, enable: bool, overwrite: bool):
    """Install a skill from URL."""
    console.print(f"[cyan]Installing skill from {url}...[/cyan]\n")
    
    try:
        result = install_skill_from_hub(
            bundle_url=url,
            version=version,
            enable=enable,
            overwrite=overwrite,
        )
        
        console.print(f"[green]✓ Skill installed successfully![/green]")
        console.print(f"  Name: {result.name}")
        console.print(f"  Enabled: {'Yes' if result.enabled else 'No'}")
        console.print(f"  Source: {result.source_url}")
        
    except Exception as e:
        console.print(f"[red]Error installing skill: {e}[/red]")


@skills_group.command("interactive")
def interactive():
    """Interactive skills management."""
    while True:
        console.print("\n[cyan]=== Skills Management ===[/cyan]")
        
        all_skills = SkillService.list_all_skills()
        available = set(list_available_skills())
        
        if not all_skills:
            console.print("[yellow]No skills found.[/yellow]")
            break
        
        # Show skills
        for i, skill in enumerate(sorted(all_skills, key=lambda s: s.name), 1):
            status = "✓" if skill.name in available else "✗"
            source = skill.source
            console.print(f"  {i:2d}. [{status}] {skill.name:<25s} ({source})")
        
        console.print()
        console.print("  [green]e[/green] - Enable/Disable skill")
        console.print("  [green]i[/green] - Show skill info")
        console.print("  [green]s[/green] - Search hub skills")
        console.print("  [green]q[/green] - Quit")
        
        choice = prompt_text("Choice", default="q").lower()
        
        if choice == "q":
            break
        elif choice == "e":
            # Toggle skill
            skill_names = [s.name for s in all_skills]
            selected = prompt_select(
                "Select skill",
                [(f"{s.name} ({s.source})", s.name) for s in sorted(all_skills, key=lambda s: s.name)],
            )
            if selected:
                is_enabled = selected in available
                if is_enabled:
                    result = SkillService.disable_skill(selected)
                    action = "disabled"
                else:
                    result = SkillService.enable_skill(selected)
                    action = "enabled"
                
                if result:
                    console.print(f"[green]✓ Skill '{selected}' {action}.[/green]")
                else:
                    console.print(f"[red]✗ Failed to {action} skill.[/red]")
                    
        elif choice == "i":
            # Show info
            skill_names = [s.name for s in all_skills]
            selected = prompt_select(
                "Select skill",
                [(f"{s.name} ({s.source})", s.name) for s in sorted(all_skills, key=lambda s: s.name)],
            )
            if selected:
                ctx = click.get_current_context()
                ctx.invoke(info_skill, name=selected)
                
        elif choice == "s":
            # Search
            query = prompt_text("Search query")
            if query:
                ctx = click.get_current_context()
                ctx.invoke(search_skills, query=query, limit=10)
        
        else:
            console.print("[yellow]Unknown command.[/yellow]")
    
    console.print("[blue]Goodbye![/blue]")
