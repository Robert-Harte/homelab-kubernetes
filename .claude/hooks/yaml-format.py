#!/usr/bin/env python3
"""Mechanical formatter for YAML files.

Applies the safe, mechanical fixes from the `yaml-best-practices` skill:
  - leading (indentation) tabs -> 2 spaces each
  - strip trailing whitespace from every line
  - normalize the file to exactly one final newline

Indentation *width* is intentionally NOT re-flowed — re-indenting nested
structures cannot be done safely without parsing intent, so that stays a
manual/reported concern.

Invocation modes, so the same formatter is the single source of truth for
Claude Code, git, and the Claude commit guard:
  - With file-path arguments (e.g. pre-commit passes the staged files): formats
    each YAML path in place.
  - With `--check` plus file-path arguments: does NOT modify anything; prints
    each path that is not already formatted and exits 1 if any need changes,
    else exits 0. Used by the PreToolUse commit guard.
  - With no arguments: reads the Claude Code PostToolUse hook JSON on stdin and
    formats the touched file.

In formatting (non-check) modes it always exits 0 so it can never block a
Claude tool call. As a pre-commit hook this means it reformats in place without
failing the commit; re-stage and the second run is a no-op.
"""
import sys
import json
import os
import re


def _reformat(original: str) -> str:
    """Return the mechanically-formatted version of YAML text."""
    fixed_lines = []
    for line in original.split("\n"):
        # convert only leading tabs (indentation) so tabs inside quoted
        # string values are left untouched
        lead = re.match(r"^[\t ]*", line).group(0)
        rest = line[len(lead):]
        line = lead.replace("\t", "  ") + rest
        # strip trailing spaces/tabs
        fixed_lines.append(line.rstrip(" \t"))
    return "\n".join(fixed_lines).rstrip("\n") + "\n"


def _read(path: str):
    """Return file text, or None if the path is not a formattable YAML file."""
    if not path or not re.search(r"\.ya?ml$", path) or not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def format_file(path: str) -> None:
    """Rewrite a single YAML file in place with the mechanical fixes."""
    original = _read(path)
    if original is None:
        return
    new = _reformat(original)
    if new != original:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
        except Exception:
            return


def needs_formatting(path: str) -> bool:
    """True if PATH is a YAML file whose content would change when formatted."""
    original = _read(path)
    return original is not None and _reformat(original) != original


def main() -> int:
    args = sys.argv[1:]

    if args and args[0] == "--check":
        # Non-mutating check mode: report files that are not yet formatted.
        unformatted = [p for p in args[1:] if needs_formatting(p)]
        for p in unformatted:
            print(p)
        return 1 if unformatted else 0

    if args:
        # CLI / pre-commit mode: each arg is a file path to format.
        for path in args:
            format_file(path)
        return 0

    # Claude Code PostToolUse hook mode: file path comes in via stdin JSON.
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    format_file((data.get("tool_input") or {}).get("file_path", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
