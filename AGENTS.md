# Rules for AI agents working on Dear ImGui Bundle

AI coding agents read this file (Claude Code through `CLAUDE.md`). It has two parts: coding guidelines, and notes on the project's development.

To write applications *with* Dear ImGui Bundle, read the guide written for AI assistants: `docs/book/intro/ai_guide.md`, published at https://imgui-bundle.pages.dev/llms.txt. Read it before writing demo or app code in this repository.

# Coding guidelines

When helping users with coding tasks, please follow these guidelines to ensure high-quality, maintainable code.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If a solution becomes complex (multiple cascading changes, need for workarounds), STOP and explain the difficulty. Present options rather than plowing ahead.

**If you encounter an API in the codebase which is awkward to use**
- Do not circumvent it with a hack. Instead, surface the issue and ask for clarification or improvement.
- The same goes for code smells or patterns that seem out of place. Don't just "make it work" - stop implementing, then communicate the underlying problem so it can be addressed properly in collaboration with the user.


**No whack-a-mole loops.** When hitting a second unexpected failure in a row on a hard problem (especially cross-platform builds, CI, toolchain issues): STOP fixing. Present the full picture of what's going wrong and why, and ask to examine the difficulties together before writing more code. Investigation time up front saves much more than it costs. Similarly, before bumping a dependency version, check changelogs/release notes for new features that could interact with existing build flags.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 3b. C++/Python Porting

When porting between C++ and Python: use raw strings for multiline content, use Python naming conventions (snake_case). Verify API names exist before using them (check the `.pyi` stubs).

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

When a bug lives in one of several sibling implementations of the same contract (e.g. several public `Setup*` entry points), check the others for the same invariant in the same change.

# For Developers

Developer documentation is in `docs/book/devel_docs/`. Read the relevant page before working on bindings, builds, forks or deployment:
- `structure.md` - Repository folder structure
- `getting_started_dev.md` - From a fresh clone to a working build
- `build_guide.md` - Build instructions and CMake options
- `build_opencv_immvision.md` - OpenCV and immvision builds
- `bindings_intro.md` - How bindings are generated (uses litgen)
- `bindings_update.md` - Updating library bindings
- `bindings_newlib.md` - Adding a new library
- `bindings_forks.md` - The forks of the libraries: branches, rebases
- `bindings_debug.md` - Debugging C++ through Python bindings
- `testing.md` - Tests
- `pypi_deploy.md` - PyPI deployment process, and the web checks before a release
- `Readme_pyodide_bundle.md` - The Pyodide build
- `cloudflare_deploy.md` - The web site's deploy

The bindings are generated automatically using [litgen](https://pthom.github.io/litgen/), a Python bindings generator for C++ libraries.

External libraries and their bindings are in `external/`:
- Each library has a submodule and a `bindings/` folder
- `external/bindings_generation/autogenerate_all.py` regenerates all bindings

## Maintenance tasks

The commands are recipes of the `justfile`: `just --list` shows them by group, each with a comment. Before doing a task by hand, look for its recipe, and read its doc:

| Task | Recipes | Doc |
|---|---|---|
| Forks and submodules | `libs_info`, `libs_check_upstream`, `libs_log <lib>`, `libs_rebase <lib>`, `libs_tag <lib>`, `libs_reattach`, `libs_fetch`, `libs_pull` | `bindings_forks.md`, `bindings_update.md` |
| Python bindings | `libs_bindings <lib>`, `libs_bindings_all` | `bindings_update.md`, `bindings_newlib.md` |
| Type checks and tests | `mypy`, `mypy_bindings_scripts`, `test_pytest`, `test_cpp_compat` | `testing.md` |
| C++ package, integration in other projects | `cpp_package_install`, `example_integration_all` | the recipes' comments |
| Web explorers (Emscripten) | `ibex_build`, `ibex_serve`, `imex_ems_build`, `imex_ems_serve`, `imex_ems_deploy` | `build_guide.md` |
| Pyodide wheel | `pyodide_setup_local_build`, `pyodide_build`, `pyodide_demo_runner` | `Readme_pyodide_bundle.md` |
| Playground | `playground_examples_docs` (the menu's descriptions, the manifests, the book's demos page), `playground_screenshots [names]` | the docstrings of `ci_scripts/playground_examples_docs.py` and `ci_scripts/playground_screenshots.py` |
| Book | `doc_serve`, `doc_build_cf`, `api_pages` (the API reference and its plain text, from the stubs) | `getting_started_dev.md` ("Build the docs"), `bindings_intro.md` ("The API pages") |
| Web site | `cf_deploy_all_in_one` (or `cf_stage_prepare`, `cf_stage`, `cf_deploy`), `cf_serve_local` | `cloudflare_deploy.md` |
| PyPI release | (CI) | `pypi_deploy.md` |

Skills (procedures for agents, in the SKILL.md format) are in `.claude/skills/`: screenshots of a GUI (`screenshot-imgui-bundle`) and driving it with the test engine (`interact-and-screenshot`), the web builds in a browser (`screenshot-web-demos`), the bindings (`regenerate-bindings`, `customize-bindings`), the forks (`fork-maintenance`). An agent that does not load them by itself can read the one a task needs.

## Code Conventions

* Autogenerated files: the content of pybind files (e.g. external/imgui/bindings/pybind_imgui.cpp) and stub files (e.g. bindings/imgui_bundle/imgui/__init__.pyi) for included libraries is mostly autogenerated.
  * Do not modify the autogenerated sections (between lines <litgen_pydef> </litgen_pydef>, <litgen_stub> </litgen_stub>).
  * Code outside of these section may be edited manually: for example the intro code before <litgen_stub> is ok to edit.
  * If something needs fixing in generated code, implement stubs or wrappers instead.
  * Regenerate with `just libs_bindings <library>`, or `just libs_bindings_all`.
  * Also generated: `external/hello_imgui/bindings/hello_imgui_amalgamation.h`, and hello_imgui's `doc_params.md` (from `doc_params.src.md`, by `tools/doc/process_md_docs.py`).

* CMake options and their corresponding C++ compile definitions use the same name, to simplify maintenance. For example, `IMGUI_BUNDLE_WITH_IMANIM_FULL_DEMOS` is both the CMake `option()` and the `#ifdef` guard in C++.

* Line length: 120 columns, in C++ and Python.

* C++ APIs: a function with several results (a status and a message, a value and an error) returns a small struct, e.g. `RenderResult { bool drawn; std::string error; }`. No output parameters: they bind badly to Python. This also holds for internal functions, which often become public later.

* Comments:
  * In public headers, say what the function does and how to call it, in one line if possible. The reasons behind it go to the .cpp file.
  * In .cpp files, keep what helps a maintainer: non-obvious invariants, workarounds. No history of how the code was found or discussed.
  * When sibling call sites pass different values of an enum or flag, pass it explicitly at every site, even where it equals the default.

* Python:
  * Silence a ruff rule with `# noqa: <code>` on the offending line. Use the per-file-ignores of `bindings/imgui_bundle/ruff.toml` only when the rule does not apply to the whole file.
  * After editing Python, run mypy on the touched files, from the repo root: mypy writes `.mypy_cache/` in the current folder, and a cache left in a demo folder gets packed into the web explorer's data.

* Demos: a flat `main()` with sensible defaults, tunables as constants at the top (with a one-line comment), a 1-2 line docstring. No argparse, no modes: the reader edits the code.
  * A demo has a module-level `gui()` (C++: `gui_<file name>()`), and a `main()` that runs it with the add-ons and configs it needs, under `if __name__ == "__main__"` (C++: `#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY`). It runs alone, and the explorer can show it in place: the explorer then gives it the same config.
  * In C++, everything but these two functions goes into an anonymous namespace: the demos of a folder are also compiled together, into one library.

## Writing docs and commits

* Docs (book pages, READMEs, docstrings):
  * Short sentences, lists for enumerations and instructions, one concern per paragraph.
  * Frame a note on the general constraint, not on the stack of the user who reported it. An example is fine.
  * Formulas in plain ASCII (`x(n+1) = r * x(n) * (1 - x(n))`) when the text may be shown as plain text.
  * No em dashes: readers take them as a sign of generated text. Use a colon, a comma, or a hyphen.
  * Markdown files: one line per paragraph and per list item, no hard wrap.
* Commit messages: a short title, a blank line, then a few body lines (what and why). Lines up to 120 columns.

## Testing

* Tests leave `*.ini` files (imgui settings) in the repo root. Remove only the untracked ones, since `pytest.ini` and `hello_imgui_example.ini` are tracked: `git ls-files --others --exclude-standard '*.ini' | xargs rm -f`.
* On macOS, GUI tests and screenshots crash at setup when the display is asleep (GLFW reports no monitor). Run `caffeinate -u -d -t 240 &` first.

## Build & Platform Notes
This project spans C++/Python with cross-platform builds (Emscripten, iOS). Be cautious about removing includes like <cstdio>: always check all platform targets before removing headers.

C++ tested only on macOS breaks on Windows CI in a few known ways:
- `<windows.h>` defines `min` and `max` macros: define `NOMINMAX` before including it, or write `(std::min)(...)`.
- Use `std::cos`, not `std::cosf` (absent from libstdc++).
- Include `<windows.h>` before `<GL/gl.h>`.

## Build folders
AI agents create their build folders inside the `builds/` folder, with a name that starts with their own prefix (`claude_` for Claude), to avoid conflicts with user-created folders.

Examples:

**Build with emscripten:**
```bash
mkdir -p builds/claude_ems && cd builds/claude_ems
source ~/emsdk/emsdk_env.sh
emcmake cmake ../.. -DCMAKE_BUILD_TYPE=Release
```

**Build the desktop imgui explorer app:**
```bash
mkdir -p builds/claude_imgui_explorer_desktop && cd builds/claude_imgui_explorer_desktop
cmake ../.. -DCMAKE_BUILD_TYPE=Release \
    -DIMGUI_BUNDLE_BUILD_IMGUI_EXPLORER_APP=ON -DIMGUI_BUNDLE_BUILD_DEMOS=OFF -DIMGUI_BUNDLE_WITH_IMMVISION=OFF
```

**Build with Python bindings + immvision (recommended for most development):**
```bash
mkdir -p builds/claude_python_bindings && cd builds/claude_python_bindings
cmake ../.. --preset "python_bindings" \
    -DPython_EXECUTABLE=/path/to/your/venv/bin/python
```
This uses the `python_bindings` preset, which enables the Python bindings (immvision is on by default). You just need to specify which Python to use. This is the most complete build for testing C++ demos, Python bindings, and immvision together.

Agents can also create build folders for specific tasks, with names that reflect the task (e.g. `claude_fix_emscripten_build` or `claude_test_pyodide`).


## Pyodide wheel filename references

The Pyodide wheel filename (e.g. `imgui_bundle-1.92.801-cp314-cp314-pyemscripten_2026_0_wasm32.whl`)
is hardcoded in several demo HTML/JS pages and a doc page. When the version
in `pyproject.toml` / `CMakeLists.txt` changes, or when the wheel platform
tag changes (see `ci_scripts/pyodide_local_build/config_versions_pyodide.sh`
runbook), every hardcoded filename must be updated. Find them with:

```bash
rg "imgui_bundle.*\.whl" --glob '!external' --glob '!builds' --glob '!dist' --glob '!*.whl' --glob '!.pyodide_build'
```

Source-of-truth files (`pyproject.toml:13`, `CMakeLists.txt:7`) carry mirror-
note comments; downstream wheel filenames live under `pyodide_projects/` and
in `docs/book/python/python_pyodide.md`. Glob-only references (`*pyemscripten*.whl`
in `justfile`, workflow yml) do not need updating on a version bump.
