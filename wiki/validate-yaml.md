---
name: validate-yaml
description: Validate that YAML files are syntactically correct. Accepts a single file or a directory (searched recursively for *.yaml and *.yml files).
---

Validate YAML files provided as an argument. If no argument is given, validate all `*.yaml` and `*.yml` files under the current working directory.

## Steps

1. **Resolve targets** — if the argument is a single file, validate that file only. If it is a directory (or omitted), use `find` to locate all `*.yaml` and `*.yml` files recursively under that path.

2. **Check required application files** — this check applies **only to application
   folders under `apps/base/`** (the Kustomize bases). Overlays such as `apps/staging/*`
   are not checked, since they intentionally inherit `deployment.yaml`/`namespace.yaml`
   from the base they reference. For each immediate subdirectory of `apps/base/` that
   contains at least one `*.yaml` or `*.yml` file, verify that all three of the following
   files are present:
   - `deployment.yaml`
   - `namespace.yaml`
   - `kustomization.yaml`

   If the target path does not include `apps/base/`, skip this check entirely.

   Record any missing files as errors for that application folder. Output a results table:

   ---

   ## Required-File Check Results

   | App Folder | deployment.yaml | namespace.yaml | kustomization.yaml | Status |
   |------------|-----------------|----------------|--------------------|--------|
   | apps/myapp | PRESENT | PRESENT | MISSING | FAIL |
   | apps/otherapp | PRESENT | PRESENT | PRESENT | PASS |

   ### Summary
   - App folders checked: N
   - Passed: N
   - Failed: N

   If any folders are missing required files, list them clearly at the end.

   ---

3. **Validate each file** — use `python3 -c "import sys, yaml; yaml.safe_load_all(open('FILE'))"` (or `yq '.' FILE > /dev/null` if yq is available) to check syntax. Catch and record any errors with the line/column info from the parser.

4. **Output a results table**:

---

## YAML Validation Results

| File | Status | Error |
|------|--------|-------|
| path/to/file.yaml | PASS | — |
| path/to/broken.yaml | FAIL | line 4, col 3: mapping values are not allowed here |

### Summary
- Files checked: N
- Passed: N
- Failed: N

If any files failed, list them again clearly at the end with their full error messages so they are easy to find and fix.

---

If no YAML files are found at the given path, say so clearly.
