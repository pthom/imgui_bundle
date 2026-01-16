# Automated bindings: introduction

The bindings are generated automatically thanks to a sophisticated generator, which is based on [srcML](https://www.srcml.org).

The generator in provided by in [litgen](https://pthom.github.io/litgen/litgen_book/00_00_intro.html) an automatic python bindings generator, developed by the same author as Dear ImGui Bundle.

## Installing the generator

See the [installation instructions](https://pthom.github.io/litgen/litgen_book/01_05_00_install_or_online.html#install-litgen-locally) (do a local installation).

## Quick information about the generator

`litgen` (aka "Literate Generator") is the package that will generate the python bindings.

Its source code is available [here](https://github.com/pthom/litgen).

It is heavily configurable by [a wide range of options](https://github.com/pthom/litgen/blob/main/src/litgen/options.py).

See for examples the [specific options for imgui bindings generation](https://github.com/pthom/imgui_bundle/blob/main/external/imgui/bindings/litgen_options_imgui.py).

## Folders structure

In order to work on bindings, it is essential to understand the folders structure inside Dear ImGui Bundle.
Please study the [dedicated doc](structure.md).


## Study of a bound library generation

Let's take the example of the library ImCoolBar.

:::{tip}
The processing of adding a new library from scratch is documented in [Adding a new library](bindings_newlib.md). It uses ImCoolBar as an example
:::

Here is how the generation works for the library. The library principal files are located in external/ImCoolBar:

```bash
external/ImCoolBar/                        # Root folder for ImCoolBar
├── ImCoolBar/                             # ImCoolBar submodule
│         ├── CMakeLists.txt               # ImCoolBar code
│         ├── ImCoolbar.cpp
│         ├── ImCoolbar.h
│         ├── LICENSE
│         └── README.md
└── bindings/                               # Scripts for the bindings generations & bindings
    ├── generate_imcoolbar.py               # This script reads ImCoolbar.h and generates:
    |                                       #     - binding C++ code in ./pybind_imcoolbar.cpp
    |                                       #     - stubs in
    |                                       #          bindings/imgui_bundle/im_cool_bar_pyi
    ├── im_cool_bar.pyi -> ../../../bindings/imgui_bundle/im_cool_bar.pyi   # this is a symlink!
    └── pybind_imcoolbar.cpp
```

The actual stubs are located here:

```bash
imgui_bundle/bindings/imgui_bundle/
├── im_cool_bar.pyi              # Location of the stubs
├── __init__.pyi                 # Main imgui_bundle stub file, which loads im_cool_bar.pyi
├── __init__.py                  # Main imgui_bundle python module which loads
|                                # the actual im_cool_bar module
├── ...
```


And the library is referenced in a global generation script:

```bash
imgui_bundle/external/bindings_generation/
├── autogenerate_all.py          # This script will call generate_imcoolbar.py (among many others)
├── all_external_libraries.py    # ImCoolBar is referenced here
├── ...
```

