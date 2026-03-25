# Adding a new library to the bindings

This example is based on the addition of [ImCoolBar](https://github.com/aiekick/ImCoolBar), which was added in Oct 2023.

## Step 1: Reference the new library

:::{tip}
All the modifications done in step 1 can be seen in [this commit](https://github.com/pthom/imgui_bundle/commit/68e6f3b3a5e812a1a3ddea275ad24296df5b7ce6).
:::

### Step 1-a: Add needed folders, files and submodules inside external/

#### Add the library as a submodule in external/lib_name/lib_name

If the library can be included without adaptations for inclusion inside ImGui Bundle, you can add it directly as a submodule.

```bash
mkdir external/ImCoolBar
git submodule add https://github.com/aiekick/ImCoolBar.git external/ImCoolBar/ImCoolBar
```


However, if it requires adaptations, you need to create a fork (it was the case for ImCoolBar):
So, the following actions were done separately:

* ImCoolBar was cloned into github.com/pthom/ImCoolBar.git
* a branch imgui_bundle was created and pushed to github. It will contain the adaptations and bug corrections for imgui_bundle.

Then, we add this fork as a submodule.

```bash
git submodule add https://github.com/pthom/ImCoolBar.git external/ImCoolBar/ImCoolBar
cd external/ImCoolBar/ImCoolBar
git checkout imgui_bundle
cd -
```


#### Create the folder external/lib_name/bindings/

Copy the folder external/bindings_generation/bindings_generator_template into external/lib_name/bindings/

```bash
cp -r external/bindings_generation/bindings_generator_template external/ImCoolBar/bindings
```

#### Rename files in external/lib_name/bindings

After having copied the template files, we need to rename them.
In the example of ImCoolbar, we will rename them as follows:

```bash
 mv external/ImCoolBar/bindings/generate_LIBNAME.py external/ImCoolBar/bindings/generate_imcoolbar.py
mv external/ImCoolBar/bindings/pybind_LIBNAME.cpp external/ImCoolBar/bindings/pybind_imcoolbar.cpp
# im_cool_bar will be the final name of the python module: imgui_bundle.im_cool_bar
mv external/ImCoolBar/bindings/LIBNAME.pyi external/ImCoolBar/bindings/im_cool_bar.pyi
```

#### Move external/ImCoolBar/bindings/im_cool_bar.pyi to bindings/imgui_bundle/

The stub file (*.pyi) _must_ be inside bindings/imgui_bundle. In order to facilitate development, we will create a symlink to it inside external/ImCoolBar/bindings/

```bash
mv external/ImCoolBar/bindings/im_cool_bar.pyi bindings/imgui_bundle/im_cool_bar.pyi
cd external/ImCoolBar/bindings/
ln -s ../../../bindings/imgui_bundle/im_cool_bar.pyi .
cd -
```

#### Final folder structure

We end up with the following structure:

```bash
external/ImCoolBar/
├── ImCoolBar/                   # Note that the submodule is inside
│         ├── CMakeLists.txt     # external/ImCoolBar/ImCoolBar/ !!!
│         ├── ImCoolbar.cpp
│         ├── ImCoolbar.h
│         ├── LICENSE
│         └── README.md
└── bindings/
    ├── im_cool_bar.pyi              # We will edit and rename those files later
    ├── generate_imcoolbar.py -> symlink to ../../../bindings/imgui_bundle/im_cool_bar.pyi
    └── pybind_imcoolbar.cpp
```

---

### Step 1-b:  Update python generator manager

**Update external/bindings_generation/all_external_libraries.py**

Add a function that returns info about this new library:

```python
def lib_imcoolbar() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImCoolBar",
        official_git_url="https://github.com/aiekick/ImCoolBar.git",
        official_branch="master",
        fork_git_url="https://github.com/pthom/ImCoolBar.git",
        fork_branch="imgui_bundle"
    )
```


```python
ALL_LIBS = [
    lib_imgui(),  # must be first as it declare bindings used by the next ones
    # ...
    lib_imcoolbar(),  # Add the lib here
    # ...
```


### Step 1-c:  Update the C++ sources to include the new lib binding generation

**In external/CMakeLists.txt:**
Add a cmake directive to compile the new library.

```cmake
# If the library is "simple" to compile you can use `add_simple_external_library_with_sources`
add_simple_external_library_with_sources(imcoolbar ImCoolBar)
```

**In external/bindings_generation/cpp/all_pybind_files.cmake:**

add `external/ImCoolBar/bindings/pybind_imcoolbar.cpp`

:::{note}
the script external/bindings_generation/autogenerate_all.py will also regenerate this file from scratch.
:::

**In external/bindings_generation/cpp/pybind_imgui_bundle.cpp:**

Add the bindings

```cpp
// ... Near the start of the file, add a new function declaration
void py_init_module_imgui_command_palette(py::module& m);
void py_init_module_implot_internal(py::module& m);
void py_init_module_imcoolbar(py::module& m);         // added this line
//  ...


void py_init_module_imgui_bundle(py::module& m)
{
    // ...

    // At the end of py_init_module_imgui_bundle, register your new python module
    auto module_imcooolbar = m.def_submodule("im_cool_bar"); // the python module will be known as imgui_bundle.im_cool_bar
    py_init_module_imcoolbar(module_imcooolbar);
```

Now, run cmake.


### Step 1-d: Edit and adapt the generation scripts

Edit the 3 files inside `external/ImCoolBar/bindings` and replace occurrences of LIBNAME with appropriate values.

### Step 1-e: Edit and adapt the imgui_bundle __init__ scripts

In bindings/imgui_bundle/__init__.py, this line was added:

```python
from imgui_bundle._imgui_bundle import im_cool_bar as im_cool_bar
```

In bindings/imgui_bundle/__init__.pyi, this line was added:

```python
from . import im_cool_bar as im_cool_bar
```


## Step 2: fine tune the generation options and write a demo

:::{tip}
All the modifications done in step 2 can be seen in [this commit](https://github.com/pthom/imgui_bundle/commit/25e6ef43c1aa8c83c8a7286cd7491b296b58de00).
:::

### Step 2-a: Edit and run `external/ImCoolBar/bindings/generate_imcoolbar.py`:

Edit and re-run it until the generated code fits the expected needs.

In the case of ImCoolBar, two simple changes were made:

```python
def main():
    # ...
    # ...

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImGui"]
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
```

Each time you run the code generation, look at `external/ImCoolBar/bindings/im_cool_bar.pyi` and `external/ImCoolBar/bindings/pybind_imcoolbar.cpp` to see if they seem OK. Also run a compilation.


### Step 2-b: Fix syntax issues in  `external/ImCoolBar/bindings/im_cool_bar.pyi`:

You can add some code before the autogenerated code to fix the syntax issues.
For example, this was added:

```python

import enum

from imgui_bundle.imgui import ImVec2, WindowFlags, WindowFlags_
ImCoolBarFlags = int
ImGuiWindowFlags = WindowFlags
ImGuiWindowFlags_None = WindowFlags_.none


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:ImCoolbar.h>    ####################
```


### Step 2-c: Write a nice looking demo

It should demo the library, and act as a tutorial, in python and C++.


## Step 3: If needed, fork and adapt the library

Some libraries require modifications to work properly with Python bindings. In such cases, you need to fork the library and make adaptations. This section describes common patterns for adapting C++ APIs for Python compatibility.

### Step 3-a: Python API compatibility macros

ImGui Bundle defines two preprocessor macros for conditional compilation when building Python bindings:

- **`IMGUI_BUNDLE_PYTHON_API`**: Code inside this block is compiled only for Python bindings. Use this to provide Python-friendly alternatives to C++ APIs.

- **`IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API`**: Code inside this block is excluded from Python bindings. Use this to hide APIs that cannot be wrapped.

**Example: Replacing pointer+size with std::vector**

Some C++ APIs use pointer + count patterns that don't translate well to Python:

```cpp
#ifdef IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API
    // This API is not usable in Python (the combination ImVec2* + int is not easily wrapped)
    IMGUI_API void  AddPolyline(const ImVec2* points, int num_points, ImU32 col, ImDrawFlags flags, float thickness);
#endif
#ifdef IMGUI_BUNDLE_PYTHON_API
    // So, we replace it with a more Python-friendly version using std::vector
    IMGUI_API void  AddPolyline(const std::vector<ImVec2>& points, ImU32 col, ImDrawFlags flags, float thickness);
#endif
```

### Step 3-b: Handling function pointer callbacks

Python bindings (via nanobind) cannot directly bind C-style function pointers. You need to provide `std::function` alternatives when building for Python.

**In the library header (e.g., `im_anim.h`):**

```cpp
// Simple callback with no user data
#ifdef IMGUI_BUNDLE_PYTHON_API
using iam_ease_fn = std::function<float(float)>;
#else
typedef float (*iam_ease_fn)(float t);
#endif

// Callbacks with void* user data - exclude user data for Python
// (Python closures capture context naturally)
#ifdef IMGUI_BUNDLE_PYTHON_API
using iam_float_resolver = std::function<float()>;
using iam_clip_callback = std::function<void(ImGuiID inst_id)>;
#else
typedef float (*iam_float_resolver)(void* user);
typedef void (*iam_clip_callback)(ImGuiID inst_id, void* user_data);
#endif
```

**Exclude void* parameters in the generator script:**

C-style callbacks often pass `void* user_data` for context. In Python, closures capture context naturally, so these parameters should be excluded.

```python
from codemanip import code_utils

options = litgen.LitgenOptions()
options.use_nanobind()

# Exclude void* parameters from function signatures
options.fn_params_exclude_types__regex = code_utils.join_string_by_pipe_char([
    r"void\s*\*",  # void* user data
])
```

**Add callback type aliases to stub files:**

The auto-generated stub file won't include nice type aliases for callbacks. Add them manually before the autogenerated section:

```python
from typing import Callable
from imgui_bundle.imgui import ImVec2, ImVec4

# Callback type aliases (add before autogenerated code)
ease_fn = Callable[[float], float]

# Resolver callbacks (return dynamic target values)
float_resolver = Callable[[], float]
vec2_resolver = Callable[[], ImVec2]
color_resolver = Callable[[], ImVec4]

# Event callbacks
clip_callback = Callable[[int], None]  # inst_id
marker_callback = Callable[[int, int, float], None]  # inst_id, marker_id, time

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# <litgen_stub> // Autogenerated code below! Do not edit!
```


### Summary of library adaptation patterns

1. **Unsupported APIs**: Hide with `#ifdef IMGUI_BUNDLE_PYTHON_UNSUPPORTED_API`
2. **Python-friendly alternatives**: Provide with `#ifdef IMGUI_BUNDLE_PYTHON_API`
3. **Function pointers**: Replace with `std::function` under `IMGUI_BUNDLE_PYTHON_API`
4. **void* user data**: Exclude from Python callbacks (closures capture context)
5. **Stub files**: Add `Callable` type aliases for documentation

