"""Web Workers for mandelbrot_engines.py, in a browser: the C++ loops on all the cores of the machine.

In a browser, Python has one thread. But the page can start Web Workers, one per core: each one runs
mandel_workers.js, which loads the same C++ compiled as a standalone WebAssembly module, and computes bands of rows.
The bands come back as messages, between two frames, and are copied into the picture's arrays.
"""
from pathlib import Path
from typing import Any

import numpy as np
from js import Blob, Float64Array, Object, URL, Uint8Array, Worker, navigator  # type: ignore
from pyodide.ffi import create_proxy, to_js  # type: ignore

HERE = Path(__file__).parent


def js_object(value: dict[str, Any]) -> Any:
    return to_js(value, dict_converter=Object.fromEntries)


class WorkerJob:
    """Some bands of a picture, computed by the workers: they land in count and size2 as they come"""

    def __init__(self, bands: list[tuple[int, int]], count: np.ndarray, size2: np.ndarray) -> None:
        self.waiting = len(bands)
        self.total = len(bands)
        self.count, self.size2 = count, size2
        self.finished: list[tuple[int, int]] = []  # the bands received, not yet taken by the engine

    def take_finished(self) -> list[tuple[int, int]]:
        bands, self.finished = self.finished, []
        return bands


class WorkerPool:
    """One Web Worker per core, started at the first job, and again after a cancel"""

    def __init__(self) -> None:
        self.size = int(navigator.hardwareConcurrency or 4)
        self.workers: list[Any] = []
        self.job: WorkerJob | None = None
        self.job_id = 0
        self.on_message = create_proxy(self.received)
        self.wasm = (HERE / "mandel_kernels_standalone.wasm").read_bytes()
        self.script_url = URL.createObjectURL(Blob.new([(HERE / "mandel_workers.js").read_text()],
                                                       js_object({"type": "text/javascript"})))

    def start_workers(self) -> None:
        wasm = Uint8Array.new(len(self.wasm))
        wasm.assign(self.wasm)
        for _ in range(self.size):
            worker = Worker.new(self.script_url)
            worker.onmessage = self.on_message
            worker.postMessage(js_object({"wasm": wasm}))
            self.workers.append(worker)

    def start(self, kernel: str, args: list[Any], w: int, h: int, max_iter: int, bands: list[tuple[int, int]],
              count: np.ndarray, size2: np.ndarray) -> WorkerJob:
        """Each worker gets one band out of `size`: the slow parts of the picture are shared"""
        if not self.workers:
            self.start_workers()
        self.job_id += 1
        self.job = WorkerJob(bands, count, size2)
        ref = None
        for i, arg in enumerate(args):
            if isinstance(arg, np.ndarray):  # the reference orbit: sent apart, as a Float64Array
                ref = Float64Array.new(arg.size)
                ref.assign(np.ascontiguousarray(arg, dtype=np.float64).ravel())
                args = [*args[:i], "ref", *args[i + 1:]]
        for k, worker in enumerate(self.workers):
            message = {"job": self.job_id, "kernel": kernel, "args": [float(a) if isinstance(a, float) else a
                                                                       for a in args],
                       "w": w, "h": h, "max_iter": max_iter, "bands": [list(b) for b in bands[k::self.size]]}
            if ref is not None:
                message["ref"] = ref
            worker.postMessage(js_object(message))
        return self.job

    def received(self, event: Any) -> None:
        """A band is done (called between two frames)"""
        data, job = event.data, self.job
        if job is None or data.job != self.job_id:
            return
        row0, row1 = int(data.row0), int(data.row1)
        data.count.assign_to(job.count[row0:row1])
        data.size2.assign_to(job.size2[row0:row1])
        job.finished.append((row0, row1))
        job.waiting -= 1

    def cancel(self) -> None:
        """Stops the workers at once: they are started again by the next job"""
        if self.job is not None and self.job.waiting > 0:
            for worker in self.workers:
                worker.terminate()
            self.workers = []
        self.job = None
