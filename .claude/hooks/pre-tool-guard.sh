#!/bin/bash
# PreToolUse guard: block destructive shell commands for the Bash tool.
# Reads the hook payload on stdin and, on a match, denies the call via the
# documented PreToolUse JSON output (permissionDecision: "deny").

INPUT=$(cat)
TOOL=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

# Destructive patterns (whitespace-tolerant).
# rm -rf / only matches root itself (slash followed by space, *, or end-of-line),
# so legitimate deletions like "rm -rf /tmp/foo" are not flagged.
DANGER='rm[[:space:]]+-(rf|fr)[[:space:]]+/([[:space:]*]|$)|git[[:space:]]+push[[:space:]]+(--force|-f)|git[[:space:]]+reset[[:space:]]+--hard|DROP[[:space:]]+TABLE'

if [ "$TOOL" = "Bash" ] && printf '%s' "$COMMAND" | grep -qE "$DANGER"; then
  jq -n --arg reason "Destructive command blocked by safety guard: $COMMAND" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$reason}}'
  exit 0
fi

# Commit gate: before letting Claude run `git commit`, ensure the staged YAML
# is already formatted, so Claude never attempts a commit the git pre-commit
# hook would reject. Mirrors the .pre-commit-config.yaml yaml-format hook using
# the same script. Skipped for amend/no-staged cases that have nothing to check.
if [ "$TOOL" = "Bash" ] && printf '%s' "$COMMAND" | grep -qE '\bgit[[:space:]]+commit\b'; then
  REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  if [ -n "$REPO_ROOT" ]; then
    # Staged, added/copied/modified YAML files (NUL-safe).
    mapfile -d '' -t STAGED_YAML < <(
      git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACM -z -- '*.yaml' '*.yml'
    )
    if [ "${#STAGED_YAML[@]}" -gt 0 ]; then
      UNFORMATTED=$(
        cd "$REPO_ROOT" &&
        python3 .claude/hooks/yaml-format.py --check "${STAGED_YAML[@]}" 2>/dev/null
      )
      if [ -n "$UNFORMATTED" ]; then
        REASON=$(printf 'These staged YAML files are not formatted and would be rejected at commit:\n%s\n\nRun: python3 .claude/hooks/yaml-format.py %s && git add %s\nthen retry the commit.' \
          "$UNFORMATTED" "$UNFORMATTED" "$UNFORMATTED")
        jq -n --arg reason "$REASON" \
          '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$reason}}'
        exit 0
      fi
    fi
  fi
fi

# Not dangerous: stay silent and let the normal permission flow proceed.
exit 0
