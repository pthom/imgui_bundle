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


// Initialize Pyodide and load packages with progress updates
async function loadPyodideAndPackages() {
    try {
        showLoadingModal();
        updateProgress(0, 'Loading Pyodide...');
        pyodide = await loadPyodide();
        const pythonVersion = pyodide.runPython("import sys; sys.version");
        console.log("Python version:", pythonVersion);

        updateProgress(20, 'Loading micropip');
        await pyodide.loadPackage("micropip");
        //await pyodide.loadPackage("micropip"); // firefox needs this to be loaded twice...
        const micropip = pyodide.pyimport("micropip");

        // SDL support in Pyodide is experimental. The flag is used to bypass certain issues.
        pyodide._api._skip_unwind_fatal_error = true;

        // Determine the base URL dynamically
        const baseUrl = `${window.location.origin}${window.location.pathname}`;
        console.log('Base URL:', baseUrl);

        // List of packages to install
        const packages = [
            // For imgui_bundle below
            // -----------------------
            '../local_wheels/imgui_bundle-1.92.705-cp313-cp313-pyemscripten_2025_0_wasm32.whl', // 4.8 MB
            'numpy', // 3.08 MB
        ];

        const totalSteps = packages.length;
        let currentStep = 1;

        for (const pkg of packages) {
            pkgName = pkg;
            // if imgui_bundle in the name, simply display "imgui_bundle" to avoid confusion with the different wheel versions
            if (pkg.includes('imgui_bundle'))
                pkgName = 'imgui_bundle';

            updateProgress(20 + (currentStep / totalSteps) * 80, `Installing ${pkgName}...`);
            await micropip.install(pkg)
            console.log(`${pkg} loaded.`);
            currentStep++;
        }

        updateProgress(100, 'All packages loaded.');
        // Optionally, add a slight delay before hiding the modal
        await new Promise(resolve => setTimeout(resolve, 500));
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
