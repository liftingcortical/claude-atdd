#!/usr/bin/env python3
"""Check that the Claude Code and Codex manifests carry the same metadata.

Run from the repository root:  python3 scripts/check-manifests.py
Exit code 0 = in sync, 1 = drift found.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"
CLAUDE_PLUGIN = ".claude-plugin/plugin.json"
CODEX_PLUGIN = ".codex-plugin/plugin.json"

PLUGIN_FIELDS = ("name", "version", "description")
MARKETPLACE_ENTRY_FIELDS = ("name", "category")


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def compare(label, claude, codex, fields):
    return [
        f"{label}: '{field}' differs (claude={claude.get(field)!r}, codex={codex.get(field)!r})"
        for field in fields
        if claude.get(field) != codex.get(field)
    ]


def claude_source_path(entry):
    return Path(entry["source"]).as_posix()


def codex_source_path(entry):
    return Path(entry["source"]["path"]).as_posix()


def check_marketplaces():
    claude = load(CLAUDE_MARKETPLACE)
    codex = load(CODEX_MARKETPLACE)
    errors = compare("marketplace", claude, codex, ("name",))

    claude_entries = {entry["name"]: entry for entry in claude["plugins"]}
    codex_entries = {entry["name"]: entry for entry in codex["plugins"]}
    if claude_entries.keys() != codex_entries.keys():
        errors.append(
            f"marketplace: plugin lists differ "
            f"(claude={sorted(claude_entries)}, codex={sorted(codex_entries)})"
        )

    for name in claude_entries.keys() & codex_entries.keys():
        claude_entry, codex_entry = claude_entries[name], codex_entries[name]
        errors += compare(f"marketplace entry '{name}'", claude_entry, codex_entry,
                          MARKETPLACE_ENTRY_FIELDS)
        if claude_source_path(claude_entry) != codex_source_path(codex_entry):
            errors.append(f"marketplace entry '{name}': source paths differ")
        errors += check_plugin(claude_source_path(claude_entry), claude_entry)
    return errors


def check_plugin(plugin_dir, claude_entry):
    claude = load(f"{plugin_dir}/{CLAUDE_PLUGIN}")
    codex = load(f"{plugin_dir}/{CODEX_PLUGIN}")
    label = f"plugin '{plugin_dir}'"
    errors = compare(label, claude, codex, PLUGIN_FIELDS)
    errors += compare(f"{label} vs claude marketplace entry", claude, claude_entry,
                      PLUGIN_FIELDS)
    return errors


def main():
    errors = check_marketplaces()
    for error in errors:
        print(f"DRIFT: {error}", file=sys.stderr)
    if not errors:
        print("Manifests in sync.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
