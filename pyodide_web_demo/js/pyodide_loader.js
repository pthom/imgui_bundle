// js/pyodide.js

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

// Initialize Pyodide and load packages with progress updates
async function loadPyodideAndPackages() {
    try {
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

        // List of packages to install
        const packages = [
            // For imgui_bundle below
            // -----------------------
            'numpy',
            'pydantic',
            'typing_extensions',
            'munch',
            'imgui_bundle',
            'pillow',

            // For fiatlight below
            // --------------------
            'pandas',
            'matplotlib',
            'opencv-python',

            // Loading Pygments, asttokens, decorator, executing, ipython, matplotlib-inline, pandas, prompt_toolkit, pure_eval, sqlite3, stack_data, traitlets, wcwidth
            // 'Pygments',
            // 'ipython',
            // 'sqlite3',

            "pyodide_dist/fiatlight-0.1.0-py3-none-any.whl",

            "scikit-learn",
            "scipy",
            "pyodide_dist/scatter_widget_bundle-0.1.0-py3-none-any.whl",
        ];

        const totalSteps = packages.length;
        let currentStep = 1;

        for (const pkg of packages) {
            updateProgress(10 + (currentStep / totalSteps) * 80, `Installing ${pkg}...`);
            await pyodide.runPythonAsync(`
import micropip;
await micropip.install('${pkg}')
            `);
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
        console.error('Pyodide not loaded yet');
        displayError('Pyodide is still loading. Please wait a moment and try again.');
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

        // Execute the code
        await pyodide.runPythonAsync(code);

        // Optionally, call a specific function
        // await pyodide.runPythonAsync('main()');

    } catch (err) {
        console.error('Caught PythonError:', err);
        displayError(err.toString());
    }
}
