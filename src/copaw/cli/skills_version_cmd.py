# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""CLI command: skills version management."""
from __future__ import annotations

import click
from rich.table import Table
from rich.console import Console

from ..agents.skills_lock import SkillsLockManager
from ..constant import WORKING_DIR

console = Console()


@click.group()
def skills_version():
    """Skills version management commands."""
    pass


@skills_version.command()
def lock():
    """Generate or update skills.lock file.
    
    Scans all active skills and records version information,
    content hashes, and source URLs for reproducible installations.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    click.echo("🔒 Generating skills.lock file...")
    lock_data = lock_mgr.generate_lock()
    
    if not lock_data["skills"]:
        click.echo("⚠️  No skills found in active_skills directory.")
        return
    
    lock_path = lock_mgr.save_lock()
    
    click.echo(f"✅ Generated lock file: {lock_path}")
    click.echo(f"📦 Locked {len(lock_data['skills'])} skill(s):")
    
    for skill_name, info in lock_data["skills"].items():
        version = info.get("version", "0.0.0")
        source = info.get("source", "unknown")
        click.echo(f"   - {skill_name} v{version} ({source})")


@skills_version.command()
def status():
    """Check for outdated skills.
    
    Compares local skill versions with remote sources (GitHub, ClawHub)
    to detect available updates.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    if not lock_mgr.lock_file.exists():
        click.echo(
            "⚠️  No skills.lock file found.\n"
            "Run 'copaw skills version lock' first."
        )
        return
    
    click.echo("🔍 Checking for skill updates...\n")
    
    outdated = lock_mgr.list_outdated_skills()
    
    if not outdated:
        click.echo("✅ All skills are up to date!")
        return
    
    # Build status table
    table = Table(title="Outdated Skills")
    table.add_column("Skill", style="cyan")
    table.add_column("Source", style="magenta")
    table.add_column("Details", style="yellow")
    
    for skill_name in outdated:
        update_info = lock_mgr.check_updates(skill_name)
        
        source = update_info.get("source", "unknown")
        details = ""
        
        if source == "github":
            details = "Content changed"
        elif source == "clawhub":
            local_v = update_info.get("local_version", "?")
            remote_v = update_info.get("remote_version", "?")
            details = f"{local_v} → {remote_v}"
        else:
            details = update_info.get("reason", "Unknown")
        
        table.add_row(skill_name, source, details)
    
    console.print(table)
    click.echo(f"\n💡 Run 'copaw skills version update' to update these skills.")


@skills_version.command()
@click.argument('skill_name', required=False)
@click.option(
    '--all',
    'update_all',
    is_flag=True,
    help='Update all outdated skills.',
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be updated without making changes.',
)
def update(skill_name: str | None, update_all: bool, dry_run: bool):
    """Update one or all outdated skills.
    
    SKILL_NAME: Name of the skill to update.
    If not provided, use --all to update all outdated skills.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    if not lock_mgr.lock_file.exists():
        click.echo(
            "⚠️  No skills.lock file found.\n"
            "Run 'copaw skills version lock' first."
        )
        return
    
    if update_all:
        # Update all outdated skills
        result = lock_mgr.update_all_skills(dry_run=dry_run)
        
        if result.get("success"):
            click.echo(
                f"✅ Updated {len(result['updated'])}/"
                f"{result['total']} skill(s)."
            )
            
            if result.get("updated"):
                click.echo("\nUpdated:")
                for skill in result["updated"]:
                    click.echo(f"   ✓ {skill}")
            
            if result.get("failed"):
                click.echo("\nFailed:")
                for skill in result["failed"]:
                    click.echo(f"   ✗ {skill}")
            
            if dry_run:
                click.echo("\n(Dry run - no changes made)")
        else:
            click.echo(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    elif skill_name:
        # Update specific skill
        click.echo(f"🔍 Checking updates for {skill_name}...")
        
        result = lock_mgr.update_skill(skill_name, dry_run=dry_run)
        
        if result.get("success"):
            if dry_run:
                click.echo(f"✅ Would update: {skill_name}")
                click.echo(f"   {result.get('message', '')}")
            else:
                click.echo(f"✅ Updated: {skill_name}")
                click.echo(f"   {result.get('message', '')}")
        else:
            click.echo(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    else:
        click.echo(
            "⚠️  Specify a skill name or use --all.\n"
            "Usage: copaw skills version update [SKILL_NAME] [--all]"
        )


@skills_version.command()
@click.argument('skill_name')
def history(skill_name: str):
    """Show version history for a skill.
    
    SKILL_NAME: Name of the skill to show history for.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    if not lock_mgr.lock_file.exists():
        click.echo(
            "⚠️  No skills.lock file found.\n"
            "Run 'copaw skills version lock' first."
        )
        return
    
    lock_data = lock_mgr.load_lock()
    
    if not lock_data or skill_name not in lock_data["skills"]:
        click.echo(f"⚠️  Skill '{skill_name}' not found in lock file.")
        return
    
    skill_info = lock_data["skills"][skill_name]
    
    click.echo(f"\n📋 Version History: {skill_name}\n")
    click.echo(f"Current Version: {skill_info.get('version', 'unknown')}")
    click.echo(f"Source: {skill_info.get('source', 'unknown')}")
    click.echo(
        f"Installed At: {skill_info.get('installed_at', 'unknown')}"
    )
    
    # TODO: Show full version history when implemented
    click.echo("\n⚠️  Full version history coming soon.")


@skills_version.command()
@click.option(
    '--show-path',
    is_flag=True,
    help='Show full path to lock file.',
)
def info(show_path: bool):
    """Show skills.lock file information.
    
    Displays lock file location, generation time, and skill count.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    if not lock_mgr.lock_file.exists():
        click.echo(
            "⚠️  No skills.lock file found.\n"
            "Run 'copaw skills version lock' first."
        )
        return
    
    lock_data = lock_mgr.load_lock()
    
    click.echo("\n📊 Skills Lock Information\n")
    
    if show_path:
        click.echo(f"Lock File: {lock_mgr.lock_file}")
    else:
        click.echo(f"Lock File: skills.lock")
    
    click.echo(
        f"Generated At: {lock_data.get('generated_at', 'unknown')}"
    )
    click.echo(f"Total Skills: {len(lock_data.get('skills', {}))}")
    click.echo(f"Lock Version: {lock_data.get('version', 1)}")
    
    # Show skill summary
    if lock_data.get("skills"):
        click.echo("\nLocked Skills:")
        for skill_name, info in lock_data["skills"].items():
            version = info.get("version", "0.0.0")
            source = info.get("source", "unknown")
            click.echo(f"   - {skill_name} v{version} ({source})")


# Add diff command for future implementation
@skills_version.command()
@click.argument('skill_name')
@click.option(
    '--remote',
    is_flag=True,
    help='Compare with remote version.',
)
def diff(skill_name: str, remote: bool):
    """Show differences for a skill.
    
    SKILL_NAME: Name of the skill to diff.
    
    Without --remote: Shows local changes since lock.
    With --remote: Shows differences from remote source.
    """
    lock_mgr = SkillsLockManager(WORKING_DIR)
    
    if not lock_mgr.lock_file.exists():
        click.echo(
            "⚠️  No skills.lock file found.\n"
            "Run 'copaw skills version lock' first."
        )
        return
    
    lock_data = lock_mgr.load_lock()
    
    if skill_name not in lock_data["skills"]:
        click.echo(f"⚠️  Skill '{skill_name}' not found in lock file.")
        return
    
    if remote:
        click.echo(
            "🔍 Comparing with remote source...\n"
            "(Feature coming soon)"
        )
        # TODO: Implement remote diff
    else:
        click.echo(
            "🔍 Checking local changes...\n"
            "(Feature coming soon)"
        )
        # TODO: Implement local diff
