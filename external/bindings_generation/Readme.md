# bindings_generation/ — Python binding generation scripts

Scripts for auto-generating Python bindings from C++ headers using [litgen](https://pthom.github.io/litgen).

**Key files:**
- `autogenerate_all.py` — Regenerate bindings for all libraries
- `all_external_libraries.py` — Registry of all external libraries (remotes, branches, forks)
- `bundle_libs_tooling/` — Helpers for submodule management
- `bindings_generator_template/` — Template for adding a new library

**Quick usage:**
```bash
just libs_bindings_all              # Regenerate all bindings
just libs_bindings <library_name>   # Regenerate one library
```

**Documentation:** [Bindings Introduction](../../docs/book/devel_docs/bindings_intro.md) | [Add New Library](../../docs/book/devel_docs/bindings_newlib.md)
