#!/usr/bin/env python3
"""Patch pyodide-build's pywasmcross.py: host-Python headers leak into the
wasm32 cross-compile on macOS with homebrew Python.

pywasmcross rewrites `-I<host python include>` arguments to point at the
cross-compile headers, by comparing the resolve()d include path against the
*unresolved* sys.prefix / sys.base_prefix. Homebrew's
/opt/homebrew/opt/python@X.Y -> ../Cellar/... symlink makes that comparison
fail, so the host headers survive into the emscripten compile, which then
aborts in pyport.h with:
    "LONG_BIT definition appears wrong for platform (bad gcc/glibc config?)."

The patch compares both the raw and resolved include path against both the
raw and resolved prefixes.

Idempotent; run inside venv_pyo (called by setup_pyodide_local_build.sh).
Remove once fixed upstream in pyodide-build (unreported as of 2026-06-12,
present in pyodide-build 0.35.0 and main).
"""
import sys
from pathlib import Path

import pyodide_build  # type: ignore[import-not-found]  # only importable inside venv_pyo

ORIGINAL = """\
    # Replace local Python include paths with the cross compiled ones
    include_path = str(Path(include_path_str).resolve())

    if include_path.startswith(sys.prefix + "/include/python"):
        return arg.replace("-I" + sys.prefix, "-I" + target_install_dir)

    if include_path.startswith(sys.base_prefix + "/include/python"):
        return arg.replace("-I" + sys.base_prefix, "-I" + target_install_dir)

    return arg
"""

PATCHED = """\
    # Replace local Python include paths with the cross compiled ones
    # PATCHED(imgui_bundle) by patch_pywasmcross_homebrew.py: compare raw and
    # resolved include paths against raw and resolved prefixes (homebrew's
    # opt -> Cellar symlink broke the original comparison).
    include_path = str(Path(include_path_str).resolve())

    prefixes = {sys.prefix, sys.base_prefix,
                str(Path(sys.prefix).resolve()), str(Path(sys.base_prefix).resolve())}
    for prefix in prefixes:
        for inc in (include_path_str, include_path):
            if inc.startswith(prefix + "/include/python"):
                return "-I" + target_install_dir + inc[len(prefix):]

    return arg
"""

MARKER = "PATCHED(imgui_bundle)"


def main() -> None:
    assert pyodide_build.__file__ is not None
    path = Path(pyodide_build.__file__).parent / "pywasmcross.py"
    text = path.read_text()
    if MARKER in text:
        print(f"pywasmcross.py already patched: {path}")
        return
    if ORIGINAL not in text:
        sys.exit(
            f"ERROR: expected code not found in {path}\n"
            "pyodide-build changed: check whether this patch is still needed, "
            "and update or delete patch_pywasmcross_homebrew.py accordingly."
        )
    path.write_text(text.replace(ORIGINAL, PATCHED))
    print(f"patched: {path}")


main()
