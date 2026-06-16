# homelab-kubernetes wiki

Documentation and runnable skill definitions for the homelab Kubernetes cluster.
Pages tagged as **skills** are fetched and executed by the `wiki-run` skill.

## Skills

- [[validate-yaml]] — validate YAML syntax and check required app files
- [[print-hello]] — minimal example skill

## Workflows

### Kubernetes validation

Run the following skills in order with `wiki-run`:

1. [[validate-yaml]] — validate the YAML files
2. [[print-hello]] — print hello world on completion

```bash
# via the wiki-run skill
wiki-run validate-yaml print-hello ./apps
```
