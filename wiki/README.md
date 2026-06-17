# Wiki source

This folder is the **source of truth** for the project's GitHub wiki
(<https://github.com/Robert-Harte/homelab-kubernetes/wiki>).

The wiki is a separate git repository, so changes here do not appear on the wiki
until they are published. The [`publish-wiki`](../.github/workflows/publish-wiki.yml)
GitHub Action publishes the contents of this folder to the wiki on every push to
`main` that touches `wiki/`.

## Rules

- **Edit pages here, not in the GitHub web UI.** Publishing is one-way
  (repo → wiki); web edits get overwritten on the next push.
- **Keep pages flat.** The wiki repo does not support subfolders cleanly. Use
  top-level `*.md` files; `-` in a filename renders as a space in the page title.
- `Home.md` is the wiki landing page.
- Files with `name`/`description` front matter (e.g. `validate-yaml.md`,
  `yaml-best-practices.md`) are skill definitions consumed by the `wiki-run` skill.

## Note

`README.md` itself is published as a wiki page named *README*. Delete it if you
don't want it on the wiki.
