---
name: wiki-run
description: Run every skill listed under the "Skills" section of the homelab-kubernetes GitHub wiki Home page, in order, against a target folder. The only argument is the folder to run against (e.g. "wiki-run ./apps"); omit it to default to the current directory.
---

# Wiki Run

Discover the skill set from the `Robert-Harte/homelab-kubernetes` GitHub wiki **Home page**,
then fetch and execute each of those skill definitions in order against a target folder. The
user no longer names individual skills — the wiki's Home page is the source of truth for which
skills run. The only argument is the folder to run against.

## Steps

1. **Resolve the target folder** — the single argument is the folder to run against
   (e.g. `./apps`). If no argument is given, default to the current directory (`.`).
   This value is forwarded to every skill that runs.

2. **Discover skills from the Home page** — fetch the wiki Home page and extract the ordered
   list of skill page names from its `## Skills` section. Each entry is a wiki link of the
   form `[[page-name]]` (or `[[page-name|Display Text]]` — use the `page-name` side):
   ```bash
   curl -fsSL "https://raw.githubusercontent.com/wiki/Robert-Harte/homelab-kubernetes/Home.md" \
     | awk '/^##[[:space:]]/{in_skills = ($0 ~ /^##[[:space:]]+Skills[[:space:]]*$/)} in_skills' \
     | grep -oE '\[\[[^]]+\]\]' \
     | sed -E 's/\[\[//; s/\]\]//; s/\|.*$//'
   ```
   This prints one skill page name per line, in the order they appear under `## Skills`.
   If the section is empty or missing, report that no skills were found on the Home page
   (`https://github.com/Robert-Harte/homelab-kubernetes/wiki/Home/_edit`) and stop.

3. **Fetch each skill page** — for every discovered skill name, download the raw markdown via:
   ```bash
   curl -fsSL "https://raw.githubusercontent.com/wiki/Robert-Harte/homelab-kubernetes/{name}.md"
   ```
   If a page returns an error or empty content, report that it does not exist and show the
   URL to create it: `https://github.com/Robert-Harte/homelab-kubernetes/wiki/{name}/_edit`.
   Continue to the next skill rather than stopping.

4. **Execute each skill in order** — for each successfully fetched markdown file, read its
   instructions and execute them exactly as if the skill were defined locally, passing the
   target folder from step 1 as the path/target argument.

5. **Report results** — after all skills have run, print a summary table:

   | Skill | Source | Result |
   |-------|--------|--------|
   | validate-yaml | https://github.com/Robert-Harte/homelab-kubernetes/wiki/validate-yaml | Passed |
   | print-hello | https://github.com/Robert-Harte/homelab-kubernetes/wiki/print-hello | Passed |
