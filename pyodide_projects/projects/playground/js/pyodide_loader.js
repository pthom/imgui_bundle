// imgui_bundle wheel source:
//   'local': self-hosted wheel in ../local_wheels/ (pinned, default for deployment)
//   'pypi' : micropip resolves the pyemscripten wheel from pypi.org (for testing)
const IMGUI_BUNDLE_WHEEL_SOURCE = 'local';
const IMGUI_BUNDLE_LOCAL_WHEEL = '../local_wheels/imgui_bundle-1.92.801-cp314-cp314-pyemscripten_2026_0_wasm32.whl';


async function load_pyodide_imgui_render() {
    console.log('Loading load_pyodide_imgui_render.py');
    try {
        const response = await fetch('py_imgui_render/pyodide_imgui_render.py');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const pythonCode = await response.text();

        // Execute the Python code
        await pyodide.runPythonAsync(pythonCode);
        // console.log('Pyodide ImGui render code loaded and executed successfully.');
    } catch (error) {
        console.error('Error in load_pyodide_imgui_render:', error);
        displayError('Failed during init (load_pyodide_imgui_render): see console for details.');
    }
}


// Debug function to test that SDL is correctly linked
// see https://github.com/pyodide/pyodide/issues/5248
async function loadPyodideAndPackages_test_daft_lib() {
    showLoadingModal();
    updateProgress(0, 'Loading Pyodide...');
    pyodide = await loadPyodide();
    const pythonVersion = pyodide.runPython("import sys; sys.version");
    updateProgress(7, 'Pyodide loaded.');
    console.log("Python version:", pythonVersion);
    await pyodide.loadPackage("micropip");
    await pyodide.loadPackage("micropip"); // firefox needs this to be loaded twice...
    updateProgress(10, 'micropip loaded.');

    // SDL support in Pyodide is experimental. The flag is used to bypass certain issues.
    pyodide._api._skip_unwind_fatal_error = true;

    // Determine the base URL dynamically
    const baseUrl = `${window.location.origin}${window.location.pathname}`;
    console.log('Base URL:', baseUrl);

    await pyodide.runPythonAsync(`
print("Before import micropip")
import micropip;
print("Before micropip.install")
await micropip.install('daft-lib')

print("Before import daft_lib")
import daft_lib
print("Before daft_lib.dummy_sdl_call")
daft_lib.dummy_sdl_call()
print("After daft_lib.dummy_sdl_call")
            `);

}


// Smoothly animate the progress bar from `startPct` toward `endPct`, never
// quite arriving (asymptote). `expectedMs` is the time at which we'll be at
// ~95% of the [start..end] span. Call .complete() when the underlying work
// finishes to snap to endPct. This is purely cosmetic — Pyodide and micropip
// don't expose real per-byte progress, so we animate against expected
// 4G timings rather than measure.
function smoothProgress(startPct, endPct, expectedMs, onUpdate) {
    const t0 = performance.now();
    const span = endPct - startPct;
    const tau = expectedMs / 3;  // 1 - exp(-3) ≈ 0.95
    let stopped = false;
    function tick() {
        if (stopped) return;
        const elapsed = performance.now() - t0;
        const pct = startPct + span * (1 - Math.exp(-elapsed / tau));
        onUpdate(pct);
        requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    return {
        complete: () => {
            stopped = true;
            onUpdate(endPct);
        },
    };
}

// Initialize Pyodide and load packages with progress updates
async function loadPyodideAndPackages() {
    try {
        showLoadingModal();

        // Phase 1: Pyodide bootstrap (~11 MB: pyodide.asm.wasm + python_stdlib.zip).
        // Animate asymptotically over ~10 s; snap when loadPyodide resolves.
        let phase1Msg = 'Downloading Python runtime (~11 MB)…';
        const phase1 = smoothProgress(0, 55, 10000,
            (pct) => updateProgress(pct, phase1Msg));
        pyodide = await loadPyodide({
            messageCallback: (m) => {
                if (typeof m === 'string' && m.length) phase1Msg = m;
            },
        });
        phase1.complete();
        const pythonVersion = pyodide.runPython("import sys; sys.version");
        console.log("Python version:", pythonVersion);

        // Phase 2: micropip — small, fast.
        updateProgress(58, 'Loading micropip…');
        await pyodide.loadPackage("micropip");
        //await pyodide.loadPackage("micropip"); // firefox needs this to be loaded twice...
        const micropip = pyodide.pyimport("micropip");

        // SDL support in Pyodide is experimental. The flag is used to bypass certain issues.
        pyodide._api._skip_unwind_fatal_error = true;

        // Phase 3: heavy wheels. Each phase animates within its own bar range.
        const imguiBundleUrl = (IMGUI_BUNDLE_WHEEL_SOURCE === 'pypi')
            ? 'imgui-bundle' : IMGUI_BUNDLE_LOCAL_WHEEL;
        const packages = [
            { url: imguiBundleUrl,
              label: 'imgui_bundle (4.9 MB)', range: [60, 85], expectedMs: 4500 },
            { url: 'numpy',
              label: 'numpy (2.8 MB)',        range: [85, 99], expectedMs: 3000 },
        ];

        for (const pkg of packages) {
            const phase = smoothProgress(pkg.range[0], pkg.range[1], pkg.expectedMs,
                (pct) => updateProgress(pct, `Installing ${pkg.label}…`));
            await micropip.install(pkg.url);
            phase.complete();
            console.log(`${pkg.url} loaded.`);
        }

        updateProgress(100, 'Ready');
        await new Promise(resolve => setTimeout(resolve, 300));
        hideLoadingModal();
        console.log('Pyodide and packages loaded.');
    } catch (error) {
        console.error('Error loading Pyodide or packages:', error);
        displayError('Failed to load Pyodide or install packages. See console for details.');
        hideLoadingModal();
    }
}

// Function to run Python code
async function runEditorPythonCode() {
    if (!pyodide) {
        // Pyodide isn't loaded yet — silently no-op. The loading banner is
        // already visible, and the Run button is disabled, so users normally
        // can't reach this path; this guard is for dropdown auto-runs.
        return;
    }

    const code = editor.getValue();

    // Clear previous errors before running new code
    clearError();

    try {
        // Redirect stdout and stderr
        pyodide.setStdout({
            batched: (s) => console.log(s),
        });
        pyodide.setStderr({
            batched: (s) => {
                console.error(s);
                displayError(s);
            },
        });

        // Stop any previous renderer *before* exec'ing the new demo's code.
        // Without this, the previous demo's animation lambda continues to
        // tick during the new module's exec (and during any awaits the new
        // demo does before calling immapp.run). It would then resolve names
        // like `gui` and `AppState` against the freshly-rebound globals from
        // the new demo, producing AttributeErrors and a cascading teardown
        // failure. See pyodide_patch_runners.stop_active_renderer for the
        // full story.
        try {
            pyodide.runPython(
                "from imgui_bundle.pyodide_patch_runners import stop_active_renderer\n" +
                "stop_active_renderer()"
            );
        } catch (e) {
            // First-load case: imgui_bundle isn't imported yet, that's fine.
            // Anything else: log and continue, the demo may still work.
            console.warn("stop_active_renderer skipped:", e);
        }

        // Write the editor code to a real file in Pyodide's VFS, and run it
        // with that filename, so that compiled-function co_filename points at
        // a real path. Without this, inspect.getsource(some_func) fails.
        // Use a unique filename per run: linecache caches by filename and
        // would otherwise return stale source after a demo is reloaded.
        const playgroundFile = `/home/pyodide/_playground_main.py`;
        pyodide.FS.writeFile(playgroundFile, code);
        await pyodide.runPythonAsync(code, { filename: playgroundFile });

    } catch (err) {
        console.error('Caught PythonError:', err);
        displayError(err.toString());
    }
}
