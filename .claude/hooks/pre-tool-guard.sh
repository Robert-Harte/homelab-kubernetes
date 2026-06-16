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

# Not dangerous: stay silent and let the normal permission flow proceed.
exit 0
