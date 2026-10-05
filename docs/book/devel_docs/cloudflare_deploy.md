# Cloudflare Pages deploy

The project publishes several static subparts to a single Cloudflare Pages project
named `imgui-bundle`, reachable at <https://imgui-bundle.pages.dev/>:

| Path                               | Contents                                                    |
|------------------------------------|-------------------------------------------------------------|
| `doc/`                             | Jupyter-book documentation (this book);                     |
| `/playground/`                     | Pyodide playground (Python examples in the browser)         |
| `/min_pyodide_app/`                | Minimal Pyodide template (single-file demo)                 |
| `/explorer/`                       | Dear ImGui Bundle Explorer (Emscripten build with OpenCV)   |
| `/local_wheels/`                   | Shared `imgui_bundle-*.whl`, loaded by the pyodide subparts |
| `doc/assets/imgui_bundle_book.pdf` | PDF export of the documentation                             |

A `_headers` file (`pyodide_projects/cf_headers`) scopes
`Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy` to `/explorer/*`
only; site-wide COI would break the playground (which pulls Pyodide and
CodeMirror from CDNs that don't set `Cross-Origin-Resource-Policy`). The same
file also sets `Content-Encoding: gzip` on `/explorer/*.data` because those
emscripten asset bundles (`application/octet-stream`) aren't auto-compressed
by the CF edge; they are pre-gzipped by `cf_stage`.


## How the deploy works

Cloudflare Pages replaces the whole site on every upload, so we maintain a
local composed staging directory (`_cf_staging/`, gitignored)
that holds the union of all subparts. `just cf_stage` refreshes the staging
tree; `just cf_deploy` uploads it via `wrangler`.

The trade-off: on every deploy the other subparts must already be present
(built) on disk. `cf_stage` does not build them — it only copies:

- Pyodide wheel: `just pyodide_build` must have run (output in `pyodide_projects/projects/local_wheels/`).
- Ibex binaries: `just ibex_build` must have run (output in `build_ibex_ems/bin/`).
- Jupyter-book docs: `just doc_build_cf` must have run (output in `docs/book/_build/html/`).


## One-time setup

1. **Install wrangler** (needs Node.js 18+):
   ```bash
   npm install -g wrangler
   ```

2. **Create an API token** at <https://dash.cloudflare.com/profile/api-tokens>
   using the **Edit Cloudflare Workers** template (it covers Pages too).

3. **Export credentials** in your shell (or your shell rc):
   ```bash
   export CLOUDFLARE_API_TOKEN=...
   export CLOUDFLARE_ACCOUNT_ID=...
   ```

4. **Verify**: `wrangler whoami` should print the account.


## Local workflow

```bash
# Build every subpart (slow: ibex with OpenCV takes 30-60 min).
# `cf_stage_prepare` runs: pyodide_setup_local_build + pyodide_build
#                        + ibex_build + doc_build_cf
just cf_stage_prepare

# Stage everything into _cf_staging, then deploy
just cf_stage
just cf_deploy

# Test the composed site locally before deploying
just cf_serve_local        # http://localhost:8764/
# → COOP/COEP headers are applied only to /explorer/* (mirrors prod)
# → Content-Encoding: gzip is applied to /explorer/*.data

# Inspect the staging tree (gitignored)
ls _cf_staging/

# Nuke staging (next deploy re-uses on-disk build outputs)
rm -rf _cf_staging
```


## CI workflow

`.github/workflows/cf_pages_deploy.yml` mirrors the local flow and is
triggered manually from the Actions tab (`workflow_dispatch`). It runs:

1. `just pyodide_setup_local_build` + `just pyodide_build` (builds the wheel)
2. `just ibex_build` (builds Emscripten binaries; slowest step, typically
   30–60 min because `IMMVISION_FETCH_OPENCV=ON` rebuilds OpenCV for wasm)
3. `just doc_build_cf` (jupyter-book HTML + PDF, needs Typst)
4. `just cf_stage` (composes the staging tree)
5. `npm install -g wrangler` + `just cf_deploy` (uploads)

Required GitHub Actions secrets: `CLOUDFLARE_API_TOKEN`,
`CLOUDFLARE_ACCOUNT_ID` (same values used locally).


## Pyodide wheel: deploy URL and filename references

The Pyodide wheel built by `just pyodide_build` is rsync'd into
`_cf_staging/local_wheels/` by `cf_stage` and ends up at:

```
https://imgui-bundle.pages.dev/local_wheels/imgui_bundle-<VERSION>-cp314-cp314-pyemscripten_2026_0_wasm32.whl
```

This URL points at the **latest** Pages deploy, not a versioned archive.
Cloudflare Pages replaces the entire site on every upload, so previous
wheels disappear when a new version is deployed. We do not promise
stability for this URL: it is convenient for quick experiments, but
docs / demos that ship to end users tell readers to download the wheel
and self-host it (GitHub release assets work as a download source even
though they cannot be passed to `micropip.install` directly — no CORS).

### When to update wheel filename references

Every time `pyproject.toml` / `CMakeLists.txt` version changes (or the wheel
platform tag changes per the runbook in
`ci_scripts/pyodide_local_build/config_versions_pyodide.sh`), the hardcoded
wheel filenames in HTML/JS/doc pages must be updated. Find them with:

```bash
rg "imgui_bundle.*\.whl" --glob '!external' --glob '!builds' --glob '!dist' --glob '!*.whl' --glob '!.pyodide_build'
```

Glob-only references (`*pyemscripten*.whl` in `justfile` and the GitHub
workflows) do not need updating on a version bump — only on a tag rename.

## The demos' API (a Worker, deployed apart)

Some demos store data on a server. The Julia map (playground: `explorables/julia_map`) lists the values of c that its users share, and their votes. They live in a Cloudflare Worker with a D1 database (Cloudflare's SQLite):

- The Worker: `imgui-bundle-api`, at <https://imgui-bundle-api.pthomet.workers.dev/julia_points>. Its code: `cloudflare/julia_points/` (`src/index.ts`, its routes are listed at the top; `wrangler.jsonc`).
- The database: `imgui_bundle_julia_points`. Its tables: `schema.sql`; its first points: `seed.sql`.
- The demo's side: `julia_points.py`, next to `julia_map.py` (`POINTS_API` is the Worker's address).

The Worker is deployed on its own, only when it changes: `just demo_julia_points_deploy` (after a type check, `just demo_julia_points_check`). The site's deploy does not touch it, and it does not touch the site.

Local tests: `just demo_julia_points_dev` runs the Worker at <http://localhost:8787/julia_points>, with a local database that holds the seed. Point `POINTS_API` there while testing. The demo on the desktop and the local playground (`pyodide_projects/serve_cors.py`) both reach it.

The admin mode: the Worker's secret `ADMIN_TOKEN` opens the routes that hide or show a point. The demo shows them when it finds the token in `JULIA_POINTS_ADMIN` (an environment variable on the desktop, `localStorage` in the browser). The token is not in this repository.

- Set it: `cd cloudflare/julia_points && wrangler secret put ADMIN_TOKEN`. `ADMIN_TOKEN` is the secret's name: the token goes at the prompt. `wrangler secret list` shows the names.
- Locally: `cloudflare/julia_points/.dev.vars` (ignored by git), with a line `ADMIN_TOKEN=<any value>`.

The database in production: `wrangler d1 execute imgui_bundle_julia_points --remote --command "SELECT ..."`, from `cloudflare/julia_points`. The free tier allows 100 000 requests a day.

## Pitfalls

- Cloudflare Pages refuses a file over 25 MiB. A stray folder can push a packed file over it: a `.mypy_cache/` left in a demo folder gets packed into the explorer's `.data` (run mypy from the repo root, and remove such caches before `just cf_stage`).
- A missing file answers 200, with an HTML page. To check that a file is deployed, look at its content type (`curl -sI <url> | grep -i content-type`), not at the status.
- After a deploy, check the live site: the book (`/doc/`) and its PDF (`/doc/assets/imgui_bundle_book.pdf`), the playground and its `examples/examples_docs.json`, the explorer, `/llms.txt`.

## Links on imgui-bundle pages at claoudflare

* [Doc & Root](https://imgui-bundle.pages.dev/doc)
* [Python Playground](https://imgui-bundle.pages.dev/playground)
* [Minimal Pyodide Template](https://imgui-bundle.pages.dev/min_pyodide_app/demo_heart.html)
* [Minimal Pyodide Template - Source](https://imgui-bundle.pages.dev/min_pyodide_app/demo_heart.source.txt)
* [ImGui Bundle Explorer](https://imgui-bundle.pages.dev/explorer)
