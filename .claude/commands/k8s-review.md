---
name: k8s-review
description: Review Kubernetes YAML manifests and provide a structured summary covering resources, security posture, and potential issues.
---

Review all Kubernetes YAML manifests in the current working directory (or the path provided as an argument).

## Steps

1. **Discover manifests** — find all `*.yaml` and `*.yml` files under the target path (default: `.`). Skip any files that are clearly not Kubernetes manifests (no `apiVersion` or `kind` field).

2. **Inventory resources** — for each manifest, record:
   - `kind` and `apiVersion`
   - `metadata.name` and `metadata.namespace` (note if namespace is missing)
   - File path

3. **Security checks** — flag any of the following:
   - Containers running as root (`runAsUser: 0` or no `securityContext`)
   - `privileged: true` or `allowPrivilegeEscalation: true`
   - Missing resource `requests` or `limits`
   - `hostNetwork: true`, `hostPID: true`, or `hostIPC: true`
   - Secrets referenced in `env` as plain `value` instead of `secretKeyRef`
   - `imagePullPolicy: Never` or images using the `latest` tag
   - Missing `readOnlyRootFilesystem: true`

4. **Reliability checks** — flag:
   - Deployments with `replicas: 1` and no PodDisruptionBudget
   - Missing liveness or readiness probes on long-running containers
   - Services of type `NodePort` or `LoadBalancer` without clear justification
   - PVCs without a `storageClassName`

5. **Networking checks** — flag:
   - Pods with no NetworkPolicy selecting them
   - Ingress resources missing TLS configuration

6. **Output a structured summary** in this format:

---

## Kubernetes Manifest Review

### Resource Inventory
| Kind | Name | Namespace | File |
|------|------|-----------|------|
| ...  | ...  | ...       | ...  |

### Security Findings
- [ ] **HIGH** `<file>`: <description>
- [ ] **MED**  `<file>`: <description>
- [ ] **LOW**  `<file>`: <description>

### Reliability Findings
- [ ] ...

### Networking Findings
- [ ] ...

### Summary
- Total manifests reviewed: N
- Total findings: N (H high, M medium, L low)
- Overall posture: PASS / NEEDS ATTENTION / CRITICAL

---

If an argument is provided (e.g. `/k8s-review ./apps/myapp`), scope the review to that path only. If no YAML files are found, say so clearly.
