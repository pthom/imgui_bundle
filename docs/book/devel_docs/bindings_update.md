# Update existing bindings

# Introduction

## Run `generate_LIBNAME.py`

The process for updating bindings for a given library is straightforward:

1. Update the library submodule in external/LIBNAME/LIBNAME
2. Run the generation script in external/LIBNAME/generate_LIBNAME.py
3. Compile and test python bindings (carefully study that nothing was broken)
4. Commit and push

For example with ImCoolBar, in order to update the bindings for ImCoolBar, one needs to run:

```bash
python external/ImCoolBar/bindings/generate_imcoolbar.py
```


## Submodules maintenance

[external/bindings_generation](https://github.com/pthom/imgui_bundle/tree/main/external/bindings_generation) contains some scripts for  the submodules maintenance.

See this extract of [external/bindings_generation/all_external_libraries.py](https://github.com/pthom/imgui_bundle/tree/main/external/bindings_generation/all_external_libraries.py), which shows that imgui and imgui_test_engine are using forks.

These forks include small modifications added for compatibility with imgui_bundle (most modifications are small changes to accommodate with python bindings).

```python
def lib_imgui() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui",
        official_git_url="https://github.com/ocornut/imgui.git",
        official_branch="docking",
        fork_git_url="https://github.com/pthom/imgui.git"
    )


def lib_imgui_test_engine() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_test_engine",
        official_git_url="https://github.com/ocornut/imgui_test_engine.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_test_engine.git",
    )
```

When using forked libraries, the git remote name for the fork is "fork", and the remote name for the official repository is "official".

**Reattach all submodules to their upstream branch**

By default, all submodules, are in mode "detached head". We need to attach them to the correct remote/branch.

We can use the utilities from external/bindings_generation:

For example, [external/bindings_generation/sandbox.py](https://github.com/pthom/imgui_bundle/tree/main/external/bindings_generation/sandbox.py) contains this:

```python
from bindings_generation import all_external_libraries

all_external_libraries.reattach_all_submodules()
```

It will reattach all submodules to the correct remote/branch.



# Example: update imgui & bindings


:::{tip}
This [video](https://youtu.be/QeBCxU7tn68) demonstrates from starts to finish the process of updating imgui and its bindings (17 minutes).
:::


## Update imgui and imgui_test_engine

**First, add a tag to our forks**

Since we will be updating our imgui and imgui_test_engine forks via a rebase, we should push a tag, so that old versions remain accessible on GitHub.

In this example, the current version of imgui_bundle is v1.0.0-beta1. So we push a "bundle_1.0.0-beta1" tag to the forks.

```bash
cd external/imgui/imgui
git tag "bundle_1.0.0-beta1"
git push fork --tags
cd -

cd external/imgui_test_engine/imgui_test_engine
git tag "bundle_1.0.0-beta1"
git push fork --tags
cd -
```

**Then rebase our forks on the official branch changes**

```bash
cd external/imgui/imgui
git rebase official/docking
cd -
```

```bash
cd external/imgui_test_engine/imgui_test_engine
git rebase official/main
cd -
```


## Run generate_imgui.py

**Run generate_imgui**

We will run [external/imgui/bindings/generate_imgui.py](https://github.com/pthom/imgui_bundle/tree/main/external/imgui/bindings/generate_imgui.py).

It will generate the python bindings for imgui, imgui_internal and imgui_test_engine.

See main() function of generate_imgui.py:

```python
def main():
    autogenerate_imgui()
    autogenerate_imgui_internal()
    autogenerate_imgui_test_engine()
```

**Examine the changes**
Look at the changes, and check if they look ok


## Compile & Test

**Correct possible compilation errors due to breaking changes in imgui's API**

**Test in C++**

Run `demo_imgui_bundle`

(demo_imgui_bundle is a global demonstration program, that uses most of the feature of all libraries)

**Test in Python**

Run `demo_imgui_bundle.py`


## Update forked submodules:

if some forked submodules required to be changed:

* tag them, push the tag
* rebase the fork branch on the official branch
* push the changes

