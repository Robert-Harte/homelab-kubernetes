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

4. **Check container ports are unique within each deployment** — this check applies
   **only to `deployment.yaml` files** among the targets; skip every other file. For
   each `deployment.yaml`, extract every
   `spec.template.spec.containers[].ports[].containerPort` value. A convenient
   extraction is:

   ```
   yq -N '.. | select(has("containerPort")) | .containerPort' deployment.yaml
   ```

   If a `deployment.yaml` declares no `containerPort`, note it and move on.

   The check is **per-app uniqueness only**: within a single `deployment.yaml`, no
   `containerPort` value may be declared more than once across that deployment's
   containers. There is **no cluster comparison** here — `containerPort` is informational
   pod-local metadata, so the same value reused by other workloads on the cluster is
   expected and fine. (Cluster-wide port conflicts are handled by the nodePort check in
   the next step.)

   Record any value that appears more than once within the same `deployment.yaml` as an
   error, and output a results table:

   ---

   ## Container-Port Check Results

   | File | containerPort | Count | Status |
   |------|---------------|-------|--------|
   | apps/base/myapp/deployment.yaml | 8080 | 2 | FAIL |
   | apps/base/myapp/deployment.yaml | 9090 | 1 | PASS |

   ### Summary
   - Deployments checked: N
   - Unique: N
   - Duplicates: N

   If any deployment declares a duplicate `containerPort`, list it clearly at the end so
   it is easy to find and change.

   ---

5. **Check Service nodePorts against the cluster** — this check applies to any target
   file that defines a `Service` (commonly `service.yaml`, but a Service may appear in
   any manifest, including a multi-document file). For each `Service`, extract every
   `spec.ports[].nodePort` value. A convenient extraction is:

   ```
   yq -N 'select(.kind == "Service") | .spec.ports[].nodePort | select(. != null)' FILE
   ```

   Unlike `containerPort`, a `nodePort` is **allocated cluster-wide** — the same value
   cannot be claimed by two different Services — so any collision is a genuine error.
   Gather the nodePorts already in use across the cluster with `kubectl` (skip this step
   gracefully and record it as **SKIPPED** if `kubectl` is unavailable or no cluster is
   reachable):

   ```
   kubectl get svc --all-namespaces -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{range .spec.ports[*]}{.nodePort}{" "}{end}{"\n"}{end}'
   ```

   As with the container-port check, **exclude the Service defined by the file itself**
   (match on `metadata.namespace` + `metadata.name`) so an already-applied Service does
   not conflict with itself. A nodePort is a conflict only when claimed by a Service with
   a *different* namespace/name.

   Record any nodePort that collides with an existing, different Service as an error, and
   output a results table:

   ---

   ## Service-NodePort Check Results

   | File | nodePort | In Use By | Status |
   |------|----------|-----------|--------|
   | apps/base/myapp/service.yaml | 30080 | default/otherapp | FAIL |
   | apps/base/myapp/service.yaml | 30090 | — | PASS |

   ### Summary
   - NodePorts checked: N
   - Available: N
   - Conflicts: N
   - Cluster check: PERFORMED / SKIPPED (reason)

   If any nodePorts conflict, list them clearly at the end with the conflicting Service so
   they are easy to find and change.

   ---

6. **Output a results table**:

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
