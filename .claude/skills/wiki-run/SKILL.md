---
name: wiki-run
description: Fetch one or more skill definitions from the homelab-kubernetes GitHub wiki and execute them in sequence. Use when the user asks to run, fetch, or list wiki skills (e.g. "wiki-run validate-yaml lint-yaml"). With no page names, list available pages.
---

# Wiki Run

Fetch one or more skill definition markdown files from the `Robert-Harte/homelab-kubernetes`
GitHub wiki and execute their instructions in sequence. The user names the wiki pages to run;
any trailing path/target arguments are forwarded to every skill that runs.

## Steps

1. **Resolve skill names** — the user provides one or more wiki page names separated by
   spaces (e.g. `validate-yaml lint-yaml`). If no page names were given, list available
   pages by cloning the wiki and listing `.md` files:
   ```bash
   git clone --depth 1 https://github.com/Robert-Harte/homelab-kubernetes.wiki.git /tmp/wiki-list 2>/dev/null \
     && ls /tmp/wiki-list/*.md | xargs -I{} basename {} .md
   ```
   Print the list and ask the user which skills to run.

2. **Fetch each wiki page** — for every skill name in the list, download the raw markdown via:
   ```bash
   curl -fsSL "https://raw.githubusercontent.com/wiki/Robert-Harte/homelab-kubernetes/{name}.md"
   ```
   If a page returns an error or empty content, report that it does not exist and show the
   URL to create it: `https://github.com/Robert-Harte/homelab-kubernetes/wiki/{name}/_edit`.
   Continue to the next skill in the list rather than stopping.

3. **Execute each skill in order** — for each successfully fetched markdown file, read its
   instructions and execute them exactly as if the skill were defined locally. Any path or
   target arguments that follow the skill names are forwarded to every skill that runs
   (e.g. "wiki-run validate-yaml lint-yaml ./apps" passes `./apps` to both skills).

4. **Report results** — after all skills have run, print a summary table:

   | Skill | Source | Result |
   |-------|--------|--------|
   | validate-yaml | https://github.com/Robert-Harte/homelab-kubernetes/wiki/validate-yaml | Passed |
   | lint-yaml | https://github.com/Robert-Harte/homelab-kubernetes/wiki/lint-yaml | Not found |
