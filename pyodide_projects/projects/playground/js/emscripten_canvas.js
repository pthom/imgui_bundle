

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

async function passCanvasToPyodide() {
    const canvas = _getEmscriptenCanvas();
    // console.log("initEmscriptenCanvas canvas:", canvas);
    // Example: Expose canvas to Python
    pyodide.canvas.setCanvas3D(canvas);  // Set canvas for 3D rendering
    // console.log("initEmscriptenCanvas canvas set");
}

// Handle canvas resizing
function passCanvasSizeToEmscripten() {
    const canvas = document.getElementById('canvas');
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    // Inform your rendering context about the resize if necessary
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('resize', passCanvasSizeToEmscripten);
    // Initial resize
    passCanvasSizeToEmscripten();
});
