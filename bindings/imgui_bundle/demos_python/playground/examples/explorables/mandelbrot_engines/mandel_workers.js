// A Web Worker of mandelbrot_engines.py, in a browser: it runs the C++ loops of mandel_kernels.cpp, compiled as a
// standalone WebAssembly module (mandel_kernels_standalone.wasm), on its own core.
//
// Messages it receives:
//   {wasm: bytes}                                   the module, once
//   {job, kernel, args, w, h, max_iter, bands, ref} some bands of rows of a picture to compute. In args, the string
//                                                   "ref" stands for the reference orbit (ref, a Float64Array).
// Messages it sends: {job, row0, row1, count, size2}, for each band, as soon as it is done.

let kernels = null;  // the module's exports, once compiled
const waiting = [];  // the jobs received before

onmessage = async (event) => {
    const message = event.data;
    if (message.wasm) {
        const imports = {env: {emscripten_notify_memory_growth: () => {}}};
        kernels = (await WebAssembly.instantiate(message.wasm, imports)).instance.exports;
        kernels._initialize();
        waiting.splice(0).forEach(run);
    } else if (kernels === null) {
        waiting.push(message);
    } else {
        run(message);
    }
};

function run(job) {
    const k = kernels, w = job.w;
    let ref = 0;
    if (job.ref) {
        ref = k.malloc(job.ref.byteLength);
        new Float64Array(k.memory.buffer, ref, job.ref.length).set(job.ref);
    }
    const args = job.args.map((arg) => (arg === "ref" ? ref : arg));
    for (const [row0, row1] of job.bands) {
        const pixels = (row1 - row0) * w;
        const count = k.malloc(pixels * 4), size2 = k.malloc(pixels * 4);
        // The loops write at [row * w + col] of the whole picture: these two arrays hold only the band, so their
        // addresses go back by row0 rows (in 32-bit arithmetic: the writes land in the arrays)
        const back = row0 * w * 4;
        k[job.kernel](...args, w, job.h, row0, row1, job.max_iter, (count - back) | 0, (size2 - back) | 0);
        const result = {
            job: job.job, row0, row1,
            count: new Int32Array(k.memory.buffer.slice(count, count + pixels * 4)),
            size2: new Float32Array(k.memory.buffer.slice(size2, size2 + pixels * 4)),
        };
        postMessage(result, [result.count.buffer, result.size2.buffer]);
        k.free(count);
        k.free(size2);
    }
    if (ref) k.free(ref);
}
