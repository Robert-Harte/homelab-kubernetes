---
name: yaml-best-practices
description: Check that YAML files follow indentation best practices — 2 spaces per indentation level and no tab characters. Accepts a single file or a directory (searched recursively for *.yaml and *.yml files).
---

Check YAML files against indentation best practices. If no argument is given, check all
`*.yaml` and `*.yml` files under the current working directory.

## Best practices enforced

1. **Use 2 spaces per indentation level** — every increase in nesting depth adds exactly
   2 spaces. Leading whitespace on any line must be a multiple of 2 spaces.
2. **Never use tabs** — tab characters must not be used for indentation (or anywhere in
   the file). Any tab should be replaced with two spaces.

## Steps

1. **Resolve targets** — if the argument is a single file, check that file only. If it is a
   directory (or omitted), use `find` to locate all `*.yaml` and `*.yml` files recursively
   under that path.

2. **Check for tabs** — flag any line that contains a tab character (`\t`). Report the file
   and line number of each occurrence. Tabs used for indentation are the priority, but flag
   tabs anywhere in the file.

3. **Check indentation width** — for each line, measure the leading spaces. Flag any line
   whose leading-space count is not a multiple of 2. Report the file, line number, and the
   offending indent width.

4. **Output a results table**:

   ---

   ## YAML Best-Practices Results

   | File | Line | Issue | Detail |
   |------|------|-------|--------|
   | apps/base/mealie/deployment.yaml | 12 | Tab character | tab used for indentation |
   | apps/base/mealie/service.yaml | 7 | Bad indent width | 3 spaces (not a multiple of 2) |

   ### Summary
   - Files checked: N
   - Files clean: N
   - Files with issues: N
   - Total issues: N (tabs: N, indent-width: N)

   ---

5. **Offer to fix** — if any issues were found, offer to fix them automatically by:
   - replacing every tab character with two spaces, and
   - reporting any remaining odd-width indentation that needs manual review (re-indenting
     nested structures is not safe to do blindly).

   Only apply fixes after the user confirms. After fixing, re-run the checks and show the
   updated results table.

If no YAML files are found at the given path, say so clearly.
