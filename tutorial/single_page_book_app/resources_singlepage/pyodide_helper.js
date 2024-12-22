// Canvas setup
// =======================================

let _gPyodide = null;

function _getEmscriptenCanvas() {
    let canvas = document.getElementById("canvas");

    // WebGL2 context check
    canvas.addEventListener("webglcontextlost", function (event) {
        alert("WebGL context lost, please reload the page");
        event.preventDefault();
    }, false);

    if (typeof WebGL2RenderingContext === 'undefined') {
        alert("WebGL 2 not supported by this browser");
        return null;
    }
    return canvas;
}

async function _passCanvasToPyodide() {
    const canvas = _getEmscriptenCanvas();
    // console.log("initEmscriptenCanvas canvas:", canvas);
    // Example: Expose canvas to Python
    _gPyodide.canvas.setCanvas3D(canvas);  // Set canvas for 3D rendering
    // console.log("initEmscriptenCanvas canvas set");
}

// Handle canvas resizing (not called at the moment)
function _passCanvasSizeToEmscripten() {
    const canvas = _getEmscriptenCanvas();
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    // Inform your rendering context about the resize if necessary
}

// GUI utilities
// ===============================================
function _showLoadingModal() {
}

function _hideLoadingModal() {
}

function _updateProgress(progress, message) {
    console.log(`Progress: ${progress} - ${message}`);
}

function _displayError(message) {
    console.error(message);
}

function _clearError() {
}

// Initial loading
//================================================


// Initialize Pyodide and load packages with progress updates
async function _loadPyodideAndPackages() {
    try {
        _showLoadingModal();
        _updateProgress(0, 'Loading Pyodide...');
        _gPyodide = await loadPyodide();
        const pythonVersion = _gPyodide.runPython("import sys; sys.version");
        _updateProgress(7, 'Pyodide loaded.');
        console.log("Python version:", pythonVersion);
        await _gPyodide.loadPackage("micropip");
        await _gPyodide.loadPackage("micropip"); // firefox needs this to be loaded twice...
        _updateProgress(10, 'micropip loaded.');

        // Important:
        // SDL support in Pyodide is experimental. The flag is used to bypass certain issues.
        _gPyodide._api._skip_unwind_fatal_error = true;

        // Determine the base URL dynamically
        const baseUrl = `${window.location.origin}${window.location.pathname}`;
        console.log('Base URL:', baseUrl);

        // List of packages to install
        const packages = [
            // For imgui_bundle below
            // -----------------------
            'numpy',  // 2.8 MB
            'pydantic', // 1.3 + 0.4 MB = 1.7 MB
            'typing_extensions', // 34 KB
            'munch', // 10 KB
            'imgui_bundle', // 9.7 MB (with 3 MB for demos_assets, 6 MB native)
            'pillow', // 964 KB

            // // For fiatlight below
            // // --------------------
            // 'requests',  // 61KB, For word count demo (we download the Hamlet text)
            // 'pandas', // 5.4 MB
            // 'matplotlib', // 6.2 MB
            // 'opencv-python', // 11 MB
            // baseUrl + `/pyodide_dist/fiatlight-0.1.0-py3-none-any.whl`, // 3.5 MB
            //
            // // For scatter_widget_bundle
            // // --------------------------
            // "scikit-learn", // 6.3 MB
            // "scipy", // 13 MB
            // baseUrl + "/pyodide_dist/scatter_widget_bundle-0.1.0-py3-none-any.whl", // 8.3 KB
        ];

        const totalSteps = packages.length;
        let currentStep = 1;

        for (const pkg of packages) {
            _updateProgress(10 + (currentStep / totalSteps) * 80, `Installing ${pkg}...`);
            await _gPyodide.runPythonAsync(`
import micropip;
await micropip.install('${pkg}')
            `);
            console.log(`${pkg} loaded.`);
            currentStep++;
        }

        _updateProgress(100, 'All packages loaded.');
        // Optionally, add a slight delay before hiding the modal
        await new Promise(resolve => setTimeout(resolve, 500));
        _hideLoadingModal();
        console.log('Pyodide and packages loaded.');
    } catch (error) {
        console.error('Error loading Pyodide or packages:', error);
        _displayError('Failed to load Pyodide or install packages. See console for details.');
        _hideLoadingModal();
    }
}

// Function to run Python code
export async function runPythonCode(code) {
    if (!_gPyodide) {
        console.error('Pyodide not loaded yet');
        displayError('Pyodide is still loading. Please wait a moment and try again.');
        return;
    }

    // Clear previous errors before running new code
    _clearError();

    try {
        // Redirect stdout and stderr
        _gPyodide.setStdout({
            batched: (s) => console.log(s),
        });
        _gPyodide.setStderr({
            batched: (s) => {
                console.error(s);
                _displayError(s);
            },
        });

        // Execute the code
        await _gPyodide.runPythonAsync(code);

        // Optionally, call a specific function
        // await pyodide.runPythonAsync('main()');

    } catch (err) {
        console.error('Caught PythonError:', err);
        _displayError(err.toString());
    }
}


//
export async function initializePyodideHelper()
{
    await _loadPyodideAndPackages();
    _passCanvasToPyodide();
}
