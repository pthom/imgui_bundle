# pthom.github.io/imgui_bundle redirector

Static redirect site for the old GitHub Pages URL
`https://pthom.github.io/imgui_bundle/*`, which now forwards to
`https://imgui-bundle.pages.dev/doc/*` (the documentation moved under
`/doc/` so the site root could host a curated landing page).

Deployed via GitHub Pages: **Settings → Pages → Branch: `main` / `/docs/pages_redirector`**.

- `index.html`: redirects the root to `imgui-bundle.pages.dev/doc/`.
- `404.html`: catches any unknown path (GitHub Pages serves `/404.html`
  for anything not found), strips the `/imgui_bundle` base prefix, and
  redirects to the same path under `imgui-bundle.pages.dev/doc`.
