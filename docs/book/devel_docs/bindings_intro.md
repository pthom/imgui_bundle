# Automated bindings: introduction

:::{tip}
If you haven't built the project yet, start with [Getting Started (Developer)](getting_started_dev.md).
:::

The bindings are generated automatically thanks to a sophisticated generator, which is based on [srcML](https://www.srcml.org).

The generator is provided by [litgen](https://pthom.github.io/litgen/) (Literate Generator), an automatic Python bindings generator developed by the same author as Dear ImGui Bundle. See also the [litgen PDF manual](https://pthom.github.io/litgen/litgen_book/litgen_book.pdf) for in-depth documentation.

## Installing the generator

See the [installation instructions](https://pthom.github.io/litgen/litgen_book/01_05_00_install_or_online.html#install-litgen-locally) (do a local installation).

## Quick information about the generator

`litgen` (aka "Literate Generator") is the package that will generate the python bindings.

Its source code is available [here](https://github.com/pthom/litgen).

It is heavily configurable by [a wide range of options](https://github.com/pthom/litgen/blob/main/src/litgen/options.py).

See for examples the [specific options for imgui bindings generation](https://github.com/pthom/imgui_bundle/blob/main/external/imgui/bindings/litgen_options_imgui.py).

## Docstrings

The docstrings of the Python API (in the stubs, and in `__doc__` at runtime) come from the comments of the C++ headers. litgen decides which comment documents which declaration:
- a comment at the end of a declaration's line documents it;
- a comment on the lines directly above a declaration documents it;
- a comment followed by an empty line is standalone: write section titles this way;
- a comment directly above several declarations on consecutive lines is a group comment: it stays standalone.

The last rule drops the docstring of a function documented on the line above, when the next function has an end-of-line comment. A header that documents each function either way can set `options.srcmlcpp_options.comment_above_is_doc_when_next_has_eol_comment = True` in its generation script, and end its section titles with an empty line. The node editor does. The option is off by default, because `imgui.h` writes its section titles directly above such pairs of functions.

Details and examples: the section "Comments and docstrings" of the litgen book's [Generated code layout](https://github.com/pthom/litgen/blob/main/docs/book/03_05_00_code_layout.ipynb) chapter.

## The API pages

The book's API reference and its plain-text version for AI assistants (`llms/api/`) are generated from the stubs by `ci_scripts/api_pages.py` (`just api_pages`; `doc_serve` and `doc_build_cf` run it). What it reads, and how to write for it:
- A module's docstring, at the top of its stub (before `<litgen_stub>`, so that a regeneration keeps it), opens its page. Its first paragraph says what the module is for: the C++ view shows it too. The next paragraphs say how to start, and what to know in Python.
- The headers' standalone comments become the page's structure. A part is a `[SECTION]` mark (imgui.h, implot.h) or a banner: a rule, a one-line title, a rule (the node editor). A section is a one-line title, or `--- Title ---`. A title is short and is not a sentence: a longer comment reads as a note.
- A header's preamble (its comments before the first title) is left out.
- A doc may use markdown (lists, code spans): the lines laid out as code or as a table are shown as text blocks.
- The libraries' table (title, tagline, modules, demos) and the per-module tables (the C++ namespaces, the "Start with" entries) are at the top of the script.
- The script also writes a JSON index of the API (`docs/book/api/json/<module>.json`: each entry with its Python and C++ names, signatures, doc, section, and the anchors of its pages). The ImGui Explorer reads it for its "API" tab: its CMake copies the modules it shows into `bin/demo_code/api_index/` at configure time, so run `just api_pages` before configuring a build of the explorer (desktop or web). Without it, the tab says that the index is not available and links to the pages.
- The C++ names come from the `/* original C++ signature */` comments of the stubs (litgen writes them for the functions, the members, and the head of each struct and enum). A function bound by hand (a custom binding with its own stub) needs this comment in its stub to appear with its C++ name.

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

## Regenerating bindings via justfile

The `justfile` provides convenient shortcuts for binding generation and library management:

```bash
just libs_bindings im_cool_bar    # Regenerate bindings for one library
just libs_bindings_all            # Regenerate all bindings
just libs_info                    # Show all libraries with their remotes
just libs_check_upstream          # Check which forks have new upstream changes
```

See [Update Bindings](bindings_update.md) for the full update workflow, and [Managing external libraries and forks](bindings_forks.md) for how forks, remotes, and bundle-specific changes are managed.

