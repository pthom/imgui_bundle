# Update existing bindings

:::{tip}
Before following this workflow, read [Managing external libraries and forks](bindings_forks.md) to understand the fork model, conventions, and available tooling.
:::

## Quick reference: justfile commands

The `justfile` provides shortcuts for the most common library management tasks:

```bash
just libs_info              # Show all libraries with their remotes (fork / official)
just libs_check_upstream    # Check which forks have new upstream changes
just libs_log <name>        # Show new upstream commits for a library
just libs_rebase <name>     # Tag current state, then rebase fork on upstream
just libs_tag <name>        # Push a date tag to a fork
just libs_bindings <name>   # Regenerate bindings for one library
just libs_bindings_all      # Regenerate all bindings
just libs_reattach          # Reattach all submodules to their branches
just libs_fetch             # Fetch all remotes
just libs_pull              # Pull all submodules
```

See [Managing external libraries and forks](bindings_forks.md) for detailed explanations of each command.

## Typical workflow

### 1. Check what's new upstream

```bash
just libs_check_upstream
```

Example output:
```
Unchanged libraries: imgui, glfw, hello_imgui, ImCoolBar, ...
Libraries with new changes in official repo: imgui_test_engine
```

Inspect the new commits:
```bash
just libs_log imgui_test_engine
```

### 2. Update the library

**For a non-forked library** (e.g. `immvision`, `glfw`):
```bash
cd external/immvision/immvision
git pull
cd -
```

**For a forked library** (e.g. `imgui_test_engine`): tag the current state, then rebase on upstream:
```bash
just libs_rebase imgui_test_engine
```

This is equivalent to:
```bash
cd external/imgui_test_engine/imgui_test_engine
git tag "bundle_$(date +%Y%m%d)"
git push fork --tags
git rebase official/main
cd -
```

### 3. Regenerate bindings

```bash
just libs_bindings imgui_test_engine
```

Or call the generation script directly:
```bash
python external/imgui_test_engine/bindings/generate_imgui_test_engine.py
```

Examine the changes in the generated `.cpp` and `.pyi` files with `git diff`.

:::{note}
A rebase without conflicts does not mean that the headers still parse. Upstream may add a macro in front of its
declarations (an export macro, a compiler hint): the parser then reads it as a part of the return type. Two signs:
the regeneration log says `Failed to run black formatter` (the stub is not valid Python any more), or the diff of the `.pyi`
file is much larger than the upstream changes (functions disappear, signatures lose their line wrapping).
Fix it in the generator options of the library: `srcmlcpp_options.functions_api_prefixes` for an API prefix,
or `srcmlcpp_options.code_preprocess_function` to remove any other macro before parsing.
:::

### 4. Compile & test

If you don't have a build directory yet, see [Getting Started](getting_started_dev.md) or [Build Guide](build_guide.md).

**Build:**
```bash
cd builds/my_build
cmake --build . -j
```

Fix any compilation errors due to breaking changes in the upstream API.
After an update of Dear ImGui, other libraries may break as well (many of them guard their code with `IMGUI_VERSION_NUM`).
Use a keep-going build to see all the errors in one pass, instead of one library at a time:
```bash
cmake --build . -j -- -k      # Makefiles (with Ninja: -- -k 0)
```

**Test in C++:**
```bash
./demo_imgui_bundle    # Global demo exercising most libraries
```

**Test in Python:**
```bash
python bindings/imgui_bundle/demos_python/demos_immapp/demo_hello_world.py
```

**Run the test suite:**
```bash
just test_pytest   # or: pytest
just test_mypy     # or: cd bindings && ./mypy_bindings.sh
```

See [Testing](testing.md) for more details.

### 5. Push fork changes (if applicable)

If the fork submodule was modified during rebase or to fix binding compatibility:
```bash
cd external/imgui_test_engine/imgui_test_engine
git push --force-with-lease fork imgui_bundle   # a rebase rewrites the history: a plain "git push" would be rejected
cd -
```

### 6. Commit

```bash
git add -A
git commit -m "Update imgui_test_engine and regenerate bindings"
```


## Example: update imgui & bindings (detailed)

:::{tip}
This [video](https://youtu.be/QeBCxU7tn68) demonstrates from start to finish the process of updating imgui and its bindings (17 minutes).
:::

imgui and imgui_test_engine use forks. The full update process:

**1. Tag current fork state**
```bash
just libs_tag imgui
just libs_tag imgui_test_engine
```

**2. Rebase forks on upstream**
```bash
just libs_rebase imgui
just libs_rebase imgui_test_engine
```

Or manually:
```bash
cd external/imgui/imgui
git rebase official/docking
cd -

cd external/imgui_test_engine/imgui_test_engine
git rebase official/main
cd -
```

**3. Regenerate bindings**

```bash
just libs_bindings_all
```

Regenerate all the libraries, not only imgui: the litgen options of imgui are shared with implot, implot3d and imgui_toggle.
For imgui itself, this runs [external/imgui/bindings/generate_imgui.py](https://github.com/pthom/imgui_bundle/tree/main/external/imgui/bindings/generate_imgui.py), which generates bindings for imgui, imgui_internal, and imgui_test_engine.

**4. Examine, build, and test** (see steps 3-4 above)

**4b. Check imgui-node-editor** (it relies on two commits of the imgui fork: see [the imgui-node-editor fork](bindings_forks.md))

Run its automated tests: they tell whether popups, combos and multiline text still work inside a node with the new Dear ImGui.
```bash
cmake -S .github/ci_automation_tests -B builds/ci_automation_tests -DCMAKE_BUILD_TYPE=Release
cmake --build builds/ci_automation_tests --target ci_node_editor_tests -j
./builds/ci_automation_tests/ci_node_editor_tests --auto     # (macOS: inside ci_node_editor_tests.app/Contents/MacOS/)
```

Then, in the node editor fork (`external/imgui-node-editor/imgui-node-editor`):
- refresh the patch files of `misc/imgui_patches/` from the two rebased imgui commits ("Context hooks..." and
  "ImGuiContext::InputTextMultilineOverride"). The command is in its `docs/fork_imgui_bundle.md`, chapter 3.
  Check them with `git apply --check` against the new upstream tags (docking and master); rebuild the `master` variant of the
  first patch by hand if its check fails.
- in its `.github/workflows/tests.yml`, bump the three pins: the imgui_bundle commit, and the docking and master tags of Dear ImGui.

**5. Push updated forks**
```bash
cd external/imgui/imgui && git push --force-with-lease fork imgui_bundle && cd -
cd external/imgui_test_engine/imgui_test_engine && git push --force-with-lease fork imgui_bundle && cd -
```
