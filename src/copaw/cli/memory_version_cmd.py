# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""CLI command: memory version management."""
from __future__ import annotations

import click
from rich.table import Table
from rich.console import Console

from ..agents.memory.version_manager import MemoryVersionManager
from ..constant import MEMORY_DIR

console = Console()


@click.group()
def memory_version():
    """Memory file version management commands."""
    pass


@memory_version.command()
@click.argument('filename')
def save(filename: str):
    """Save current version of a memory file.
    
    FILENAME: Name of the memory file (e.g., MEMORY.md).
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    try:
        version_path = version_mgr.save_version(
            filename,
            message=f"Manual save via CLI",
        )
        
        click.echo(f"✅ Saved version: {version_path}")
        
    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
    except Exception as e:
        click.echo(f"❌ Failed to save version: {e}")


@memory_version.command()
@click.argument('filename')
@click.option(
    '--limit',
    default=10,
    help='Maximum number of versions to show.',
)
def list(filename: str, limit: int):
    """List available versions for a memory file.
    
    FILENAME: Name of the memory file.
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    versions = version_mgr.list_versions(filename, limit=limit)
    
    if not versions:
        click.echo(f"⚠️  No versions found for '{filename}'.")
        return
    
    # Build table
    table = Table(title=f"Versions of {filename}")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Message", style="green")
    table.add_column("Size", style="yellow", justify="right")
    
    for i, version in enumerate(versions, start=1):
        timestamp = version.get("timestamp", "Unknown")[:19]  # Shorten
        message = version.get("message", "")[:40] or "-"
        size = version.get("content_length", version.get("size", 0))
        
        table.add_row(
            str(i),
            timestamp,
            message,
            f"{size} chars",
        )
    
    console.print(table)
    click.echo(f"\n💡 Use 'copaw memory version restore' to restore a version.")


@memory_version.command()
@click.argument('version_path')
@click.option(
    '--no-backup',
    is_flag=True,
    help='Skip creating backup before restore.',
)
def restore(version_path: str, no_backup: bool):
    """Restore a memory file from a version.
    
    VERSION_PATH: Path to the version file.
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    try:
        restored_path = version_mgr.restore_version(
            version_path,
            backup=not no_backup,
        )
        
        if no_backup:
            click.echo(f"✅ Restored: {restored_path}")
        else:
            click.echo(
                f"✅ Restored: {restored_path}\n"
                f"   (Backup created before restore)"
            )
        
    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
    except Exception as e:
        click.echo(f"❌ Failed to restore: {e}")


@memory_version.command()
@click.argument('version_path1')
@click.argument('version_path2')
def diff(version_path1: str, version_path2: str):
    """Compare two versions.
    
    VERSION_PATH1: Path to first version file.
    VERSION_PATH2: Path to second version file.
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    try:
        diff_output = version_mgr.diff_versions(
            version_path1,
            version_path2,
        )
        
        if diff_output:
            click.echo("\n📊 Version Diff:\n")
            click.echo(diff_output)
        else:
            click.echo("✅ No differences found.")
        
    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
    except Exception as e:
        click.echo(f"❌ Failed to diff: {e}")


@memory_version.command()
@click.argument('version_path')
def diff_current(version_path: str):
    """Compare a version with current file.
    
    VERSION_PATH: Path to the version file.
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    try:
        diff_output = version_mgr.diff_with_current(version_path)
        
        if diff_output:
            click.echo("\n📊 Diff with Current:\n")
            click.echo(diff_output)
        else:
            click.echo("✅ No differences from current.")
        
    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
    except Exception as e:
        click.echo(f"❌ Failed to diff: {e}")


@memory_version.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be deleted without making changes.',
)
@click.option(
    '--max-versions',
    default=10,
    help='Maximum versions to keep per file.',
)
def cleanup(dry_run: bool, max_versions: int):
    """Clean up old versions.
    
    Removes excess versions, keeping only the most recent N versions
    per file (default: 10).
    """
    version_mgr = MemoryVersionManager(MEMORY_DIR, max_versions=max_versions)
    
    click.echo(
        f"🧹 Cleaning up old versions "
        f"(keeping max {max_versions} per file)...\n"
    )
    
    result = version_mgr.cleanup(dry_run=dry_run)
    
    if result["deleted"]:
        click.echo(f"🗑️  Deleted {result['deleted_count']} version(s):")
        for path in result["deleted"][:10]:  # Show first 10
            click.echo(f"   - {path}")
        if result["deleted_count"] > 10:
            click.echo(f"   ... and {result['deleted_count'] - 10} more")
    else:
        click.echo("✅ No versions to delete.")
    
    click.echo(f"\n📦 Kept {result['kept_count']} version(s).")
    
    if dry_run:
        click.echo("\n(Dry run - no changes made)")


@memory_version.command()
def info():
    """Show memory version system information."""
    version_mgr = MemoryVersionManager(MEMORY_DIR)
    
    click.echo("\n📊 Memory Version Information\n")
    click.echo(f"Memory Directory: {version_mgr.memory_dir}")
    click.echo(f"Version Directory: {version_mgr.version_dir}")
    click.echo(f"Max Versions Per File: {version_mgr.max_versions}")
    
    # Count total versions
    if version_mgr.version_dir.exists():
        total_versions = len(
            list(version_mgr.version_dir.iterdir())
        )
        click.echo(f"Total Versions Stored: {total_versions}")
    else:
        click.echo("Total Versions Stored: 0")
