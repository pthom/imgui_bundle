"""
Catch Python exceptions raised inside Test.test_func / gui_func / teardown_func.

Why
---
The ImGui Test Engine runs test callbacks on its own coroutine thread (C++).
A Python exception raised inside one of those callbacks becomes a
`nanobind::python_error` that unwinds into C++. With nothing to catch it,
the C++ runtime calls `std::terminate()` -> `abort()` and the whole process
dies — even if other tests were registered and unrelated.

This module replaces the property setters for the three callback slots on
`imgui.test_engine.Test` so that, at the moment the user assigns a callable,
we wrap it in a guard that:
  1. Calls the user's function normally.
  2. If it raises (BaseException, so SystemExit and KeyboardInterrupt too):
     - prints the full Python traceback to stderr;
     - reports the failure to the engine via `ImGuiTestEngine_Error(...)`
       so the test is recorded as an *error* (distinct from a check failure);
     - swallows the exception so the engine's coroutine thread keeps running
       and remaining tests in the queue still execute.

After install(), `Test.test_func = my_func` transparently stores a wrapped
version of `my_func`. The user does not need to know this module exists.

Engine API references (from `imgui.test_engine`):
  - error(file: str, func: str, line: int, flags: TestCheckFlags, fmt: str) -> bool
        Wraps `ImGuiTestEngine_Error()`. Records an error on the currently
        running test (marks it `TestStatus.error`). Returns True if the engine
        accepted the report. The `file`/`func`/`line` are surfaced in the
        engine's UI log; we pass synthetic values since the real Python
        location is already in the traceback we just printed.
  - TestCheckFlags_.none
        No special handling. Other flags (e.g. SilentSuccess) exist but are
        irrelevant for an error report.
"""

from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    # Avoid circular import at runtime: this module is imported from
    # `imgui_bundle/__init__.py` during its own initialization.
    from imgui_bundle.imgui import test_engine as _te
    TestCallback = Callable[[_te.TestContext], None]
    ErrorFn = Callable[[str, str, int, _te.TestCheckFlags, str], bool]


# Marker set on functions we've already wrapped, so repeated read-then-write
# cycles (`t.f = t.f`) do not stack wrappers.
_WRAPPED_MARK = "_imgui_bundle_safe_test_callback"

# The three callback attributes on `Test` that need wrapping.
_CALLBACK_ATTRS = ("test_func", "gui_func", "teardown_func")


def install(test_engine_module: Any) -> None:
    """Patch `imgui.test_engine.Test` so callback assignments are guarded.

    Idempotent: calling twice is safe (the wrapped marker prevents
    double-wrapping individual callbacks, and re-installing the property
    overwrites with an equivalent property).
    """
    Test = test_engine_module.Test
    error_fn = test_engine_module.error                       # see module docstring
    none_flag = test_engine_module.TestCheckFlags_.none       # no special flags

    for attr_name in _CALLBACK_ATTRS:
        existing = Test.__dict__.get(attr_name)
        if not isinstance(existing, property) or existing.fset is None:
            # Either the attribute doesn't exist on this build, or it's not
            # a writable property. Skip silently rather than fail at import.
            continue

        guarded_setter = _make_guarded_setter(existing.fset, attr_name, error_fn, none_flag)
        setattr(Test, attr_name, property(existing.fget, guarded_setter))


def _make_guarded_setter(
    original_setter: Callable[[Any, Any], None],
    attr_name: str,
    error_fn: "ErrorFn",
    none_flag: Any,
) -> Callable[[Any, Any], None]:
    """Return a setter that wraps the incoming callable before delegating."""

    def guarded_setter(self: Any, fn: Any) -> None:
        # Pass through None/already-wrapped values unchanged. nanobind itself
        # will reject None at the binding layer if that type is not allowed,
        # which preserves the original error behavior.
        if fn is None or getattr(fn, _WRAPPED_MARK, False):
            original_setter(self, fn)
            return
        original_setter(self, _wrap_callback(fn, attr_name, error_fn, none_flag))

    return guarded_setter


def _wrap_callback(
    fn: "TestCallback",
    attr_name: str,
    error_fn: "ErrorFn",
    none_flag: Any,
) -> "TestCallback":
    """Return a function with the same signature that catches any exception."""

    def wrapped(ctx: Any) -> None:
        try:
            fn(ctx)
        except BaseException:
            # Print the full traceback so the user sees their actual error.
            tb_text = traceback.format_exc()
            sys.stderr.write(
                f"\n[ImGui Test Engine] Python exception in {attr_name}:\n{tb_text}"
            )
            sys.stderr.flush()
            # Tell the engine: this test errored out. Marks the test as
            # TestStatus.error in the engine's report. We pass "<python>" as
            # file and `attr_name` as func because the real location is in
            # the traceback above and the engine just needs *something* to
            # show in its log.
            try:
                error_fn(
                    "<python>",
                    attr_name,
                    0,
                    none_flag,
                    f"Python exception in {attr_name} (see traceback above)",
                )
            except BaseException:
                # Defensive: if `error_fn` itself fails (e.g. no live test
                # context), do not propagate — the whole point of this
                # wrapper is to never let an exception escape.
                pass

    setattr(wrapped, _WRAPPED_MARK, True)
    return wrapped
