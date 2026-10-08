---
name: screenshot-web-demos
description: See and drive the WEB builds of imgui_bundle (Emscripten explorers, Pyodide playground and pages) in Chrome - screenshots, a few clicks, and reading versions from inside Pyodide - or in an iPhone simulator (Safari, touch). Use for the web checks before a release, or to validate a change that only shows in the browser or on a touch screen. Rarely needed. Ask the user before launching the browser or the simulator, unless their rules allow it.
---

# Screenshot and drive the web demos

The two other screenshot skills (`screenshot-imgui-bundle`, `interact-and-screenshot`) only see desktop windows.
This one opens the **web builds** in Chrome through Playwright: it can take screenshots, click at canvas coordinates,
and run Python inside a Pyodide page.

## Entry points

- Builds (the user's job, long): `ibex_build`, `imex_ems_build`, `pyodide_build`. Servers: `ibex_serve`, `imex_ems_serve`, `pyodide_serve_projects`, `pyodide_demo_runner` (the first three depend on the builds: start the servers directly, see "Servers").
- Docs: `docs/book/devel_docs/pypi_deploy.md` ("Web checks before a release"), `cloudflare_deploy.md` (the deployed site, and how to check it).

## Which change needs which rebuild

- A Python demo or a playground file (HTML, CSS, JS, `examples.json`): no rebuild. The playground serves the demo folders through symlinks (`pyodide_projects/projects/playground/demos_immapp` and the like), so a served page shows the edit on reload.
- A change in hello_imgui, immapp or a C++ library (the bindings' module included): three builds, independent of each other, so run them in parallel, each in its own background job: the Pyodide wheel (`just pyodide_build`, about 15 minutes; from another folder: `just --justfile <repo>/justfile --working-directory <repo> pyodide_build`), the bundle explorer (`just ibex_build`, incremental in `build_ibex_ems`), and any Emscripten bench of yours (`cmake --build builds/claude_<name>_ems --target <demo>`, with `source ~/emsdk/emsdk_env.sh` first). A new source file in a globbed folder needs a reconfigure (`cmake .` in the build folder) before the build.
- A C++ demo of the explorer: the explorer only (`just ibex_build`); its page bundles the demos' assets only if its CMake target says so (`hello_imgui_bundle_assets_from_folder`).
- The desktop Python module: `cmake --build builds/python_bindings` (it copies the module into the venv); a new source file there needs a reconfigure, which collides with CLion's: ask the user to pause CLion first.

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

Then `Read` the PNG files. Actions: `wait:SECONDS`, `move:X,Y`, `click:X,Y`, `down:X,Y`, `up`, `wheel:DX,DY`, `key:KEYS`,
`shot:NAME`, `py:EXPRESSION`, `js:EXPRESSION` (see the docstring of the script). A widget held by the mouse (a slider while
dragged): `click:BLANK_X,BLANK_Y down:X,Y move:X2,Y shot:held up` (the first click: see "Gotchas"). `--console` prints the page's console (Pyodide's
stdout/stderr, wasm aborts). The context has clipboard permissions: `"js:navigator.clipboard.readText()"` after
clicking a copy button checks what the app wrote (a JS promise is awaited). Viewport: 1400 x 900, device scale 1, so coordinates read on a screenshot can be used as is; `--viewport 480x800` for a phone.

## A setting before the app starts (a theme)

A Hello ImGui app reads its ini file at startup, from the page's in-memory file system. A copy of the page, written next to
it in the build's `bin/` folder (never in the repo), can write that file before the app starts. For a theme, replace
`preRun:[]` in the copy with:

```js
preRun:[function(){FS.writeFile("/Power_save.ini", ";;;<<<HelloImGui_Misc>>>;;;\n[Theme]\nName=ImGuiColorsLight\n")}]
```

- The ini's name is the window title, each character other than a letter or a digit replaced by `_` ("Power save" gives `Power_save.ini`), unless the app sets `iniFilename`.
- The theme names are those of `ImGuiTheme_Name()` (`ImGuiColorsLight`, `DarculaDarker`, `MaterialFlat`...). One copy per theme gives the dark and light checks of the same page.

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

## iPhone simulator (Safari, touch)

For what only a touch screen shows: the touch layer, `ImGuiConfigFlags_IsTouchScreen`, a phone's width. It needs a Mac with Xcode. The simulator reaches the Mac's servers at `localhost`, a secure context, so the threaded builds work there (the bundle explorer included), unlike a phone on the local network.

```bash
xcrun simctl list devices available | grep iPhone     # pick one, note its UDID
xcrun simctl boot <udid> && open -a Simulator        # a visible window
xcrun simctl openurl booted http://localhost:8642/demo_imgui_bundle.html
xcrun simctl io booted screenshot /tmp/web_shots/sim.png
idb ui tap --udid <udid> X Y                          # in points: the screenshot's pixels / 3 (iPhone 17: 1206 x 2622 px)
xcrun simctl shutdown <udid>                          # when done
```

- Taps need idb (Meta's iOS Development Bridge), installed by the user: `brew install facebook/fb/idb-companion` (Homebrew asks to trust the tap's formula first), then `uv tool install fb-idb --python 3.13`. Its taps reach the ImGui canvas as touches; `idb ui swipe` and `idb ui text` exist too. `idb ui describe-point` finds nothing on the canvas (it has no accessibility tree): harmless.
- Wait between the steps: the wasm startup takes a few seconds, and idling lowers the frame rate after 3 s. A small Python script with `time.sleep` between the `simctl` calls does it.
- `simctl io screenshot` reads the simulator itself: it works even where macOS blocks `screencapture` for the terminal.
- Other sessions may be using the simulator: check `xcrun simctl list devices booted` first. A device you did not boot belongs to someone else: ask before driving it. Name your device by its UDID (`openurl <udid>`, `io <udid>`), not `booted`.
- A screenshot during a drag (a held slider): start `idb ui swipe --udid <udid> X1 Y X2 Y --duration 4` in the background, and take the screenshot about 2 s later.
- A swipe that starts on a widget that takes the drags (a code block, a plot) goes to that widget, not to the page: start it on text or on blank space.
- With a page zoom set in Safari (other than 100%), the canvas sometimes keeps the unzoomed size at the first load: the content is cut on the right and the end of the page hides under the toolbar. Reload.

## Gotchas

- **Never use plain `chrome --headless --screenshot`** on these pages: it writes the image but never exits (the render loop
  keeps the page busy). The helper closes the browser itself and has a hard `--timeout` (150 s by default).
- **Prefer seeing to clicking.** Clicks use pixel coordinates read on a previous screenshot: they break when a layout changes.
  Take a screenshot first, read the coordinates, then click. For Pyodide, prefer `py:` checks: they are exact.
- ImGui needs the mouse move on one frame and the button on the following ones: the helper handles it (move, wait, down, up, wait).
- **An Emscripten page sometimes loses its first press** (about 1 run in 5 on 2026-10-08, the cause unknown; 14 runs out of 14 fine after a first click). Start with a click on blank space before the clicks or the holds that matter, and check the result on the screenshot (a held slider's frame changes color).
- Playwright draws no mouse cursor: in a visible run, only ImGui's hover highlight shows where the mouse is.
- `uv run` needs `--no-project`, otherwise it tries to build imgui_bundle itself.
- **One browser run at a time.** Two concurrent `drive_page.py` runs gave non-deterministic pages (sections opened by
  themselves in the Pyodide tour); sequential runs of the same actions are deterministic.
- The servers: `rm -f *.gz` fails in zsh when there is no `.gz` file (no match), which kills the `&&` chain: skip it.
- Pyodide demo runner (`just pyodide_demo_runner`, port 6789, `?file=demo_imgui_md.py`) runs any file of
  `demos_python` with the local wheel; it does not expose `window.pyodide`, so `py:` does not work there.
- Shortcuts on macOS (Chrome and Firefox): Cmd, on the Emscripten GLFW pages and on the Pyodide (SDL) pages alike (`io.config_mac_osx_behaviors` is True in both): drive them with `key:Meta+...` (e.g. `key:Meta+f` for a rich_md document's find, which `key:Control+f` does not open).
- A phone on the local network reaches the servers at the Mac's address (`http://192.168.x.y:<port>`). There the browser ignores COOP/COEP (an http origin other than localhost is not secure), so a page built with threads waits forever at "Initializing". A bundle build with `IMGUI_BUNDLE_BUILD_DEMOS` builds every page with threads (for the test engine): the explorer and the demos' own pages alike. The playground works (Pyodide). For a phone: the iPhone simulator (above), a deploy (https), or a build without threads, in a folder of its own. That build needs a temporary local edit, never committed: in `imgui_bundle_cmake/imgui_bundle_build_lib.cmake`, `if (IMGUI_BUNDLE_BUILD_DEMOS)` becomes `if (IMGUI_BUNDLE_BUILD_DEMOS AND NOT IMGUI_BUNDLE_TMP_NO_PTHREAD)`; configure with `-DIMGUI_BUNDLE_TMP_NO_PTHREAD=ON -DHELLOIMGUI_EMSCRIPTEN_PTHREAD=OFF -DHELLOIMGUI_EMSCRIPTEN_PTHREAD_ALLOW_MEMORY_GROWTH=OFF -DHELLOIMGUI_WITH_TEST_ENGINE=OFF`, build the demo's target, then revert the edit. The revert makes that folder reconfigure at its next build, with threads again: a rebuild needs the edit again.
- If macOS shows a warning attributed to the IDE hosting the terminal when Chrome starts, stop and tell the user
  (seen once; probable cause: Chrome had a pending update. It did not come back after Chrome was restarted).
