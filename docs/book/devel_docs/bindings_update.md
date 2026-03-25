# Update existing bindings

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

### 4. Compile & test

If you don't have a build directory yet, see [Getting Started](getting_started_dev.md) or [Build Guide](build_guide.md).

**Build:**
```bash
cd builds/my_build
cmake --build . -j
```

Fix any compilation errors due to breaking changes in the upstream API.

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
git push fork
cd -
```

### 6. Commit

```bash
git add -A
git commit -m "Update imgui_test_engine and regenerate bindings"
```


## Submodule management

[external/bindings_generation/all_external_libraries.py](https://github.com/pthom/imgui_bundle/tree/main/external/bindings_generation/bundle_libs_tooling/all_external_libraries.py) contains the registry of all external libraries. Each library has an `official` remote (upstream) and optionally a `fork` remote (pthom's fork with binding-compatibility patches).

```bash
just libs_info    # See all libraries, their remotes, and paths
```

Example output:
```
NAME                  FORK                                              OFFICIAL                                            PATH
imgui                 https://github.com/pthom/imgui.git                https://github.com/ocornut/imgui.git                external/imgui/imgui
imgui_test_engine     https://github.com/pthom/imgui_test_engine.git    https://github.com/ocornut/imgui_test_engine.git    external/imgui_test_engine/imgui_test_engine
glfw                                                                    https://github.com/glfw/glfw.git                    external/glfw/glfw
hello_imgui                                                             https://github.com/pthom/hello_imgui.git            external/hello_imgui/hello_imgui
...
```

Libraries without a fork URL are used directly from upstream.

**Reattach submodules:** By default, submodules are in "detached HEAD" mode. To attach them to their correct remote/branch:
```bash
just libs_reattach
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
just libs_bindings imgui
```

This runs [external/imgui/bindings/generate_imgui.py](https://github.com/pthom/imgui_bundle/tree/main/external/imgui/bindings/generate_imgui.py), which generates bindings for imgui, imgui_internal, and imgui_test_engine.

**4. Examine, build, and test** (see steps 3-4 above)

**5. Push updated forks**
```bash
cd external/imgui/imgui && git push fork && cd -
cd external/imgui_test_engine/imgui_test_engine && git push fork && cd -
```
