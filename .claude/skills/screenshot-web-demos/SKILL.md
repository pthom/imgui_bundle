---
name: screenshot-web-demos
description: See and drive the WEB builds of imgui_bundle (Emscripten explorers, Pyodide playground and pages) in Chrome - screenshots, a few clicks, and reading versions from inside Pyodide. Use for the web checks before a release, or to validate a change that only shows in the browser. Rarely needed. Ask the user before launching the browser, unless their rules allow it.
---

# Screenshot and drive the web demos

The two other screenshot skills (`screenshot-imgui-bundle`, `interact-and-screenshot`) only see desktop windows.
This one opens the **web builds** in Chrome through Playwright: it can take screenshots, click at canvas coordinates,
and run Python inside a Pyodide page.

## Entry points

- Builds (the user's job, long): `ibex_build`, `imex_ems_build`, `pyodide_build`. Servers: `ibex_serve`, `imex_ems_serve`, `pyodide_serve_projects`, `pyodide_demo_runner` (the first three depend on the builds: start the servers directly, see "Servers").
- Docs: `docs/book/devel_docs/pypi_deploy.md` ("Web checks before a release"), `cloudflare_deploy.md` (the deployed site, and how to check it).

## Rules (do not skip)

1. **Ask before launching the browser**, unless the user's rules allow it: say which pages you will open, and that a
   Chrome window will appear.
2. **Visible by default.** `--headless` only if the user agreed to an invisible run.
3. **Local pages only** (`localhost`). The helper refuses anything else unless `--allow-remote`, which needs an explicit request.
4. **Throwaway profile, throwaway environment.** The helper uses the installed Chrome with a temporary profile
   (never the user's), and Playwright comes from `uv run --no-project --with playwright`: nothing is installed in the
   project's Python environment.
5. **Stop everything you started** (servers, browser), check it, and say it in your report, with the list of pages opened.

## Servers

The `just ..._serve` recipes depend on the (long) builds: start the servers directly, in the background, and stop them after.
The builds themselves are the user's job (`just ibex_build`, `just imex_ems_build`, `just pyodide_build`).

```bash
# (with the project's Python environment active)
# ImGui Explorer (imgui / implot / implot3d manual), port 7006
cd build_imex_ems/bin && exec python ../../ci_scripts/webserver_multithread_policy.py -p 7006
# ImGui Bundle Explorer, port 8642 -> http://localhost:8642/demo_imgui_bundle.html
cd build_ibex_ems/bin && exec python ../../ci_scripts/webserver_multithread_policy.py -p 8642
# Pyodide pages (playground, local_wheels, min_pyodide_app, ...), port 6456
cd pyodide_projects/projects && exec python ../serve_cors.py --port 6456
```

Stop one with `pkill -f "webserver_multithread_policy.py -p 7006"` (or `"serve_cors.py --port 6456"`), then check the port
with `curl`. The background task is then reported as failed (exit 144): this is your own `pkill`.

## The helper: `drive_page.py`

```bash
SK=.claude/skills/screenshot-web-demos
OUT=/tmp/web_shots              # any scratch folder: never the repo

# Emscripten: wait for the wasm startup, screenshot, open "Widgets", screenshot
uv run --no-project --with playwright python $SK/drive_page.py http://localhost:7006/ --out $OUT \
    wait:6 shot:start click:74,229 shot:widgets

# Pyodide: read the versions from inside the page (no pixels involved), then screenshot
uv run --no-project --with playwright python $SK/drive_page.py http://localhost:6456/playground/ --out $OUT \
    wait:40 "py:__import__('imgui_bundle').__version__" "py:__import__('imgui_bundle').imgui.get_version()" shot:playground
```

Then `Read` the PNG files. Actions: `wait:SECONDS`, `move:X,Y`, `click:X,Y`, `wheel:DX,DY`, `key:KEYS`, `shot:NAME`,
`py:EXPRESSION`, `js:EXPRESSION` (see the docstring of the script). `--console` prints the page's console (Pyodide's
stdout/stderr, wasm aborts). The context has clipboard permissions: `"js:navigator.clipboard.readText()"` after
clicking a copy button checks what the app wrote (a JS promise is awaited). Viewport: 1400 x 900, device scale 1, so coordinates read on a screenshot can be used as is; `--viewport 480x800` for a phone.

## What to check

The pages and what each of them must show are listed in `docs/book/devel_docs/pypi_deploy.md`, section
"Web checks before a release". Reminder: `min_pyodide_app/demo_heart.html` installs `imgui-bundle` from PyPI, so it shows the
last *released* version.

A runner for the whole checklist (servers, screenshots, version checks, contact sheet) was not built, on purpose: the
maintainer chose this skill alone. Revisit at a release if the checks feel repetitive.

## Firefox (a browser-specific check)

`--browser firefox` opens Playwright's own Firefox instead of Chrome (a one-time `uv run --no-project --with playwright
playwright install firefox`, about 100 MB in `~/Library/Caches/ms-playwright`). For what differs between browsers only
(the API pages' anchors in Firefox, 2026-10-04); the clipboard checks work in Chrome only.

## Gotchas

- **Never use plain `chrome --headless --screenshot`** on these pages: it writes the image but never exits (the render loop
  keeps the page busy). The helper closes the browser itself and has a hard `--timeout` (150 s by default).
- **Prefer seeing to clicking.** Clicks use pixel coordinates read on a previous screenshot: they break when a layout changes.
  Take a screenshot first, read the coordinates, then click. For Pyodide, prefer `py:` checks: they are exact.
- ImGui needs the mouse move on one frame and the button on the following ones: the helper handles it (move, wait, down, up, wait).
- Playwright draws no mouse cursor: in a visible run, only ImGui's hover highlight shows where the mouse is.
- `uv run` needs `--no-project`, otherwise it tries to build imgui_bundle itself.
- **One browser run at a time.** Two concurrent `drive_page.py` runs gave non-deterministic pages (sections opened by
  themselves in the Pyodide tour); sequential runs of the same actions are deterministic.
- The servers: `rm -f *.gz` fails in zsh when there is no `.gz` file (no match), which kills the `&&` chain: skip it.
- Pyodide demo runner (`just pyodide_demo_runner`, port 6789, `?file=demo_imgui_md.py`) runs any file of
  `demos_python` with the local wheel; it does not expose `window.pyodide`, so `py:` does not work there.
- Copy shortcut in Chrome on macOS: Cmd+C on the Emscripten GLFW pages, Ctrl+C on the Pyodide (SDL) pages.
- If macOS shows a warning attributed to the IDE hosting the terminal when Chrome starts, stop and tell the user
  (seen once; probable cause: Chrome had a pending update. It did not come back after Chrome was restarted).
