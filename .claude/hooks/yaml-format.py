#!/usr/bin/env python3
"""PostToolUse formatter for YAML files.

Reads the hook JSON on stdin, and if the touched file is a *.yaml/*.yml file,
applies the safe, mechanical fixes from the `yaml-best-practices` skill:
  - leading (indentation) tabs -> 2 spaces each
  - strip trailing whitespace from every line
  - normalize the file to exactly one final newline

Indentation *width* is intentionally NOT re-flowed — re-indenting nested
structures cannot be done safely without parsing intent, so that stays a
manual/reported concern. Always exits 0 so it can never block a tool call.
"""
import sys
import json
import os
import re


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not re.search(r"\.ya?ml$", path) or not os.path.isfile(path):
        return 0

    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception:
        return 0

    fixed_lines = []
    for line in original.split("\n"):
        # convert only leading tabs (indentation) so tabs inside quoted
        # string values are left untouched
        lead = re.match(r"^[\t ]*", line).group(0)
        rest = line[len(lead):]
        line = lead.replace("\t", "  ") + rest
        # strip trailing spaces/tabs
        fixed_lines.append(line.rstrip(" \t"))

    new = "\n".join(fixed_lines).rstrip("\n") + "\n"

    if new != original:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
        except Exception:
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
