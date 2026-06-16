# homelab-kubernetes wiki

Documentation and runnable skill definitions for the homelab Kubernetes cluster.
Pages tagged as **skills** are fetched and executed by the `wiki-run` skill.

## Skills

- [[validate-yaml]] — validate YAML syntax and check required app files
- [[print-hello]] — minimal example skill

## Workflows

```bash
# via the wiki-run skill
wiki-run validate-yaml print-hello ./apps
```
