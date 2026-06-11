# Managing external libraries and forks

:::{tip}
This page explains the fork model, conventions, and tooling for managing ImGui Bundle's external libraries. For the step-by-step update workflow, see [Update existing bindings](bindings_update.md). For adding a new library, see [Adding a new library](bindings_newlib.md).
:::

## Direct vs. forked libraries

ImGui Bundle includes ~24 external C++ libraries. Each lives under `external/<LibName>/` and is typically a git submodule.

Some libraries can be used as-is from their upstream repository. Others need modifications to work with Python bindings — for example, replacing `pointer + count` C APIs with `std::vector`, or swapping C function pointers for `std::function`. In those cases, a **fork** is maintained on GitHub under [github.com/pthom](https://github.com/pthom).

Run `just libs_info` to see the full picture:

```
NAME                      FORK                                                  OFFICIAL                                              PATH
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
imgui                     https://github.com/pthom/imgui.git                    https://github.com/ocornut/imgui.git                  external/imgui/imgui
imgui_test_engine         https://github.com/pthom/imgui_test_engine.git        https://github.com/ocornut/imgui_test_engine.git      external/imgui_test_engine/imgui_test_engine
glfw                                                                            https://github.com/glfw/glfw.git                      external/glfw/glfw
hello_imgui                                                                     https://github.com/pthom/hello_imgui.git              external/hello_imgui/hello_imgui
im_cool_bar               https://github.com/pthom/ImCoolBar.git                https://github.com/aiekick/ImCoolBar.git              external/ImCoolBar/ImCoolBar
im_file_dialog            https://github.com/pthom/ImFileDialog.git             https://github.com/dfranx/ImFileDialog.git            external/ImFileDialog/ImFileDialog
imgui_command_palette     https://github.com/pthom/imgui-command-palette.git    https://github.com/hnOsmium0001/imgui-command-palette.git external/imgui-command-palette/imgui-command-palette
imgui_knobs               https://github.com/pthom/imgui-knobs.git              https://github.com/altschuler/imgui-knobs             external/imgui-knobs/imgui-knobs
imgui_node_editor         https://github.com/pthom/imgui-node-editor.git        https://github.com/thedmd/imgui-node-editor.git       external/imgui-node-editor/imgui-node-editor
imgui_md                  https://github.com/pthom/imgui_md.git                 https://github.com/mekhontsev/imgui_md                external/imgui_md/imgui_md
md4c                                                                            https://github.com/mity/md4c                          external/imgui_md/md4c
imgui_microtex            https://github.com/pthom/MicroTeX.git                 https://github.com/NanoMichael/MicroTeX.git           external/imgui_microtex/MicroTeX
imgui_tex_inspect         https://github.com/pthom/imgui_tex_inspect.git        https://github.com/andyborrell/imgui_tex_inspect.git  external/imgui_tex_inspect/imgui_tex_inspect
imgui_toggle              https://github.com/pthom/imgui_toggle.git             https://github.com/cmdwtf/imgui_toggle.git            external/imgui_toggle/imgui_toggle
imgui_color_text_edit     https://github.com/pthom/ImGuiColorTextEdit.git       https://github.com/goossens/ImGuiColorTextEdit.git    external/ImGuiColorTextEdit/ImGuiColorTextEdit
imguizmo                  https://github.com/pthom/ImGuizmo.git                 https://github.com/CedricGuillemet/ImGuizmo.git       external/ImGuizmo/ImGuizmo
immvision                                                                       https://github.com/pthom/immvision.git                external/immvision/immvision
implot                    https://github.com/pthom/implot.git                   https://github.com/epezent/implot.git                 external/implot/implot
implot3d                  https://github.com/pthom/implot3d.git                 https://github.com/brenocq/implot3d.git               external/implot3d/implot3d
nanovg                    https://github.com/pthom/nanovg.git                   https://github.com/memononen/nanovg.git               external/nanovg/nanovg
im_anim                   https://github.com/pthom/ImAnim.git                   https://github.com/soufianekhiat/ImAnim.git           external/ImAnim/ImAnim
```

- Libraries with a **FORK** column are maintained as forks with bundle-specific patches.
- Libraries with only an **OFFICIAL** column are used directly from upstream.
- A few internal libraries (e.g. `immapp`, `imgui_explorer`) have no git URL — they live directly in the repo.

### When is a fork created?

A fork is created when a library needs C++ source modifications that cannot be achieved through the binding generator alone. Typical reasons:

- **Python API adaptations**: replacing `pointer + size` patterns with `std::vector`, C function pointers with `std::function`, `const char*` with `std::optional<std::string>`, etc.
- **Bug fixes** or behavior changes specific to ImGui Bundle's usage.
- **Build adaptations** for cross-platform support.

If a library can be bound without source modifications, it is used directly from upstream (no fork needed).


## The fork branch model

### Branches and remotes

Each forked library has **two git remotes**:

| Remote | Points to | Branch tracked |
|--------|-----------|----------------|
| `official` | Upstream author's repo (e.g. `ocornut/imgui`) | The upstream branch (e.g. `docking`, `master`, `main`) |
| `fork` | pthom's fork (e.g. `pthom/imgui`) | `imgui_bundle` |

The fork branch is always named **`imgui_bundle`**. All bundle-specific changes live on this branch.

Non-forked libraries have a single `official` remote pointing to their upstream repo.

:::{note}
Dear ImGui tracks the **`docking`** branch of upstream (not `master`), since ImGui Bundle uses the docking-enabled version. The fork branch is still `imgui_bundle`.
:::

### Rebase, not merge

When updating a fork to incorporate new upstream changes, we **rebase** the `imgui_bundle` branch on top of the latest upstream — we do not merge. This keeps the bundle-specific diff small, self-contained, and easy to review. It also makes future rebases easier since there are no merge commits to carry forward.

The typical update sequence is:

1. **Tag** the current fork state (safety snapshot): `just libs_tag <name>`
2. **Rebase** the fork branch on upstream: `just libs_rebase <name>`
3. **Force-push** the rebased branch to the fork remote (if the rebase changed anything)

See [Update existing bindings](bindings_update.md) for the full step-by-step workflow.


## Marking bundle-specific changes

### In code: `[ADAPT_IMGUI_BUNDLE]` markers

All bundle-specific modifications in forked library source code are bracketed with comment markers:

```cpp
// [ADAPT_IMGUI_BUNDLE]
// ... bundle-specific code ...
// [/ADAPT_IMGUI_BUNDLE]
```

This makes it easy to find all bundle adaptations by searching for `ADAPT_IMGUI_BUNDLE`, and to review the diff against upstream.

**Example from `imgui.h`** — adding a Python-friendly overload:

```cpp
//[ADAPT_IMGUI_BUNDLE]
IMGUI_API void ShowDemoWindow_MaybeDocked(
    bool create_window, bool* p_open = NULL,
    ImGuiWindowFlags initial_extra_flags = 0,
    ImVec2 window_pos = ImVec2(0, 0), ImVec2 window_size = ImVec2(0, 0));
//[/ADAPT_IMGUI_BUNDLE]
```

### In commits: `[Bundle]` prefix

Bundle-specific commits use a **`[Bundle]`** prefix in the commit message. This clearly distinguishes them from upstream commits when reading the git log:

```
$ git log --oneline (imgui fork)
8f3f4c6 [Bundle] Add python API for SetWindowFocus(optional<string>)
4a7d77e [Bundle] imgui_demo.cpp: imgui_manual -> imgui explorer
245cc3e [Bundle] Python API for SliderFloat2/4, InputFloat2/4, ColorEdit3/4, ColorPicker3/4
f6ba577 [Bundle] imgui_demo.cpp: move demo marker / Layout/Stack Layout into TreeNode
8e8f3ed [Bundle]: add ShowDemoWindow_MaybeDocked (with flags & position)
...
```

Some older commits may use `[ADAPT_IMGUI_BUNDLE]` as the prefix — this is equivalent.

### Preprocessor macros

Two preprocessor macros control conditional compilation in forked code:

- **`IMGUI_BUNDLE_PYTHON_API`**: Code inside `#ifdef IMGUI_BUNDLE_PYTHON_API` is compiled **only** when building Python bindings. Use this to provide Python-friendly alternatives.

- **`IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API`**: Code inside this guard is **excluded** from Python bindings (it is always defined, but the binding generator skips it). Use this to hide C++ APIs that cannot be wrapped.

These are often used together to swap an unwrappable API for a Python-friendly one:

```cpp
// From imgui-node-editor — replacing pointer+size with std::vector
#ifdef IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API
IMGUI_NODE_EDITOR_API int GetSelectedNodes(NodeId* nodes, int size);
IMGUI_NODE_EDITOR_API int GetSelectedLinks(LinkId* links, int size);
#endif
#ifdef IMGUI_BUNDLE_PYTHON_API
IMGUI_NODE_EDITOR_API std::vector<NodeId> GetSelectedNodes();
IMGUI_NODE_EDITOR_API std::vector<LinkId> GetSelectedLinks();
#endif
```

```cpp
// From imgui.h — replacing function pointer with std::function
#ifdef IMGUI_BUNDLE_PYTHON_API
using ImGuiInputTextCallback = std::function<int(ImGuiInputTextCallbackData*)>;
#else
#ifdef IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API
typedef int (*ImGuiInputTextCallback)(ImGuiInputTextCallbackData* data);
#endif
#endif
```

See [Adding a new library](bindings_newlib.md) (Step 3) for more adaptation patterns.

### Contributing fixes upstream

If a fix or improvement is **not** specific to ImGui Bundle (e.g. a genuine bug fix, a useful feature), it should be contributed upstream:

- **Do not** use `[Bundle]` prefix or `[ADAPT_IMGUI_BUNDLE]` markers.
- **Do not** use `IMGUI_BUNDLE_PYTHON_API` / `IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API` guards.
- Submit a PR to the upstream repository.
- Once merged upstream, the fix will be picked up during the next rebase.


## Tooling

### Python module: `bundle_libs_tooling`

The library management logic lives in `external/bindings_generation/bundle_libs_tooling/`:

| File | Purpose |
|------|---------|
| `all_external_libraries.py` | Central registry — defines all ~24 libraries as `ExternalLibrary` instances in the `ALL_LIBS` list. Contains functions for bulk operations (reattach, fetch, pull, check upstream). |
| `external_library.py` | `ExternalLibrary` dataclass — holds name, git URLs, branches, remote names, and provides methods for git operations (add remotes, fetch, rebase, tag, etc.). |
| `shell_commands.py` | `ShellCommands` helper — runs multiline shell commands with echo and error handling. |

The `ExternalLibrary` dataclass fields:

```python
@dataclass
class ExternalLibrary:
    name: str                          # Library name (e.g. "ImCoolBar")
    official_git_url: Optional[str]    # Upstream repo URL
    official_branch: str = "master"    # Upstream branch to track
    fork_git_url: Optional[str]        # Fork repo URL (None if not forked)
    fork_branch: str = "imgui_bundle"  # Fork branch (always "imgui_bundle")
    is_published_in_python: bool       # Whether this lib gets Python bindings
    is_sub_library: bool               # Sub-library (e.g. md4c inside imgui_md)
```

### Justfile recipes: `just libs_*`

The `justfile` at the repo root wraps the Python tooling into convenient commands:

| Command | Description |
|---------|-------------|
| `just libs_info` | Show all libraries with their remotes and paths |
| `just libs_reattach` | Reattach all submodules to their correct branches and remotes |
| `just libs_fetch` | Fetch all remotes for all submodules |
| `just libs_pull` | Pull all submodules |
| `just libs_check_upstream` | Check which forked libraries have new upstream changes |
| `just libs_log <name>` | Show new upstream commits not yet in a fork |
| `just libs_tag <name>` | Push a dated tag (`bundle_YYYYMMDD`) to a fork |
| `just libs_rebase <name>` | Tag current state, then rebase fork branch on upstream |
| `just libs_bindings <name>` | Regenerate Python bindings for one library |
| `just libs_bindings_all` | Regenerate all Python bindings |

Library names can be passed in snake_case or original form (e.g. `just libs_log imgui` or `just libs_log ImGuiColorTextEdit`).


## Common operations

### After a fresh clone: reattach submodules

By default, git submodules are in "detached HEAD" mode. To set up the correct remotes (`official` / `fork`) and attach each submodule to its tracking branch:

```bash
just libs_reattach
```

This is typically the **first thing to do** after cloning the repository when you plan to work on library updates.

### Check what's new upstream

```bash
just libs_check_upstream
```

Example output:
```
Unchanged libraries: glfw, hello_imgui, ImCoolBar, ImFileDialog, imgui-command-palette, ...
Libraries with new changes in official repo: imgui, imgui_test_engine, ImGuiColorTextEdit
```

Then inspect the new commits for a specific library:
```bash
just libs_log imgui
```

### Tag a fork (safety snapshot)

Before rebasing, create a dated tag so you can recover the previous state:

```bash
just libs_tag imgui
```

This creates a tag named `bundle_YYYYMMDD` and pushes it to the fork remote.

### Rebase a fork on upstream

```bash
just libs_rebase imgui
```

This command:
1. Creates a dated tag (safety snapshot)
2. Fetches both `official` and `fork` remotes
3. Checks out the `imgui_bundle` branch
4. Rebases it on top of `official/<upstream_branch>`

If the rebase introduces changes, you need to **force-push** manually:
```bash
cd external/imgui/imgui
git push fork --force-with-lease
cd -
```

### Update a non-forked library

For libraries without a fork, simply pull:
```bash
cd external/glfw/glfw
git pull
cd -
```

Or pull all submodules at once:
```bash
just libs_pull
```
