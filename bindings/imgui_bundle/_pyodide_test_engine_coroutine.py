# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""The test engine's coroutine in Pyodide: a Pyodide task, switched with JSPI (`pyodide.ffi.run_sync`).

Called from C++ (`external/bindings_generation/cpp/pybind_test_engine_pyodide.cpp`), which forwards
`ImGuiTestCoroutineInterface` here:
- `create(main_func, name)`: a task that waits for its first `run()`, then calls `main_func()`;
- `run(coroutine)`: resumes the task, and blocks until it yields or ends. Returns False once it has ended;
- `yield_()`: from the task, hands control back to the caller of `run()`, and blocks until the next `run()`.

`run_sync` only works inside a task: `pyodide_patch_runners` renders its frames from one.
"""
import asyncio
from typing import Any, Callable, Optional

import js  # type: ignore
from pyodide.ffi import run_sync  # type: ignore


class _Coroutine:
    def __init__(self, main_func: Callable[[], None], name: str) -> None:
        self.name = name
        self.main_func = main_func
        self.terminated = False
        self.resume: Any = js.Promise.withResolvers()  # resolved by run()
        self.yielded: Any = None  # resolved when the task yields or ends
        self.task = asyncio.ensure_future(self._main())

    async def _main(self) -> None:
        await self.resume.promise
        try:
            self.main_func()
        finally:
            self.terminated = True
            self.yielded.resolve()


# The coroutine that runs now (the engine runs only one at a time)
_running: Optional[_Coroutine] = None


def create(main_func: Callable[[], None], name: str) -> _Coroutine:
    return _Coroutine(main_func, name)


def run(coroutine: _Coroutine) -> bool:
    global _running
    if coroutine.terminated:
        return False
    resume, coroutine.yielded = coroutine.resume, js.Promise.withResolvers()
    previous, _running = _running, coroutine
    resume.resolve()
    try:
        run_sync(coroutine.yielded.promise)
    finally:
        _running = previous
    return not coroutine.terminated


def yield_() -> None:
    coroutine = _running
    assert coroutine is not None, "yield_() can only be called from the coroutine"
    yielded, coroutine.resume = coroutine.yielded, js.Promise.withResolvers()
    yielded.resolve()
    run_sync(coroutine.resume.promise)
