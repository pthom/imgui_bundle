// ===========================
// Layouting: tooltips, editor
// ===========================


// =====================================
// Initialize Split.js and CodeMirror
// =====================================
// Initialize Split.js for resizable panes
Split(['#editor-container', '#canvas-container'], {
    sizes: [25, 75], // Adjusted sizes as per user's update
    minSize: 0,    // Minimum size of each pane in pixels
    gutterSize: 8,
    cursor: 'col-resize',
    onDrag: () => {
        onSplitDrag();
    }
});

function onSplitDrag() {
    // Trigger window resize event, so that Emscripten can adjust its canvas size
    window.dispatchEvent(new Event('resize'));
}

// Initialize CodeMirror for the code editor
const editor = CodeMirror(document.getElementById('editor'), {
    mode: 'python',
    lineNumbers: true,
    theme: 'eclipse', // Optional: Change theme as desired
    value: ""
});

// Adjust CodeMirror size to fill the container
editor.setSize('100%', '100%');


// =====================================
// Initialize Tippy.js tooltips with HTML content
// =====================================

// Initialize Tippy.js tooltips with HTML content
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Tippy.js tooltips');
    try {
        tippy('.logo', { // now this should work
            allowHTML: true,
            placement: 'bottom',
            animation: 'scale',
            arrow: true,
            delay: [100, 100],
            theme: 'light-border',
        });
    } catch (error) {
        console.error('Error loading Tippy.js:', error);
    }
});

// =====================================
// Editor toolbar: Run button, shortcut, modified indicator
// =====================================
const runButton = document.getElementById('run-button');
runButton.addEventListener('click', async () => {
    await runEditorPythonCode();
    _lastRunCode = editor.getValue();
    runButton.classList.remove('needs-run');
});

// Show platform-appropriate shortcut hint
const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
document.getElementById('run-shortcut').textContent = isMac ? '⌘↵' : 'Ctrl+Enter';

// Keyboard shortcut: Ctrl+Enter (or Cmd+Enter on Mac)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (runButton.disabled) return;  // Pyodide not ready yet
        runEditorPythonCode();
    }
});

// Track modifications: compare editor content to last loaded code
let _lastLoadedCode = '';
let _lastRunCode = '';

function setLoadedCode(code) {
    _lastLoadedCode = code;
    _lastRunCode = code;
    document.getElementById('editor-modified').classList.remove('visible');
    runButton.classList.remove('needs-run');
}

editor.on('change', () => {
    const currentCode = editor.getValue();
    const modifiedFromFile = currentCode !== _lastLoadedCode;
    const needsRun = currentCode !== _lastRunCode;
    document.getElementById('editor-modified').classList.toggle('visible', modifiedFromFile);
    runButton.classList.toggle('needs-run', needsRun);
});

// Mark code as run
const _origRunEditorPythonCode = runEditorPythonCode;
runEditorPythonCode = async function() {
    await _origRunEditorPythonCode();
    _lastRunCode = editor.getValue();
    runButton.classList.remove('needs-run');
};

// Update the editor toolbar label
function setEditorLabel(label) {
    document.getElementById('editor-label').textContent = label;
}


// =====================================
// Loading banner: lazy video + rotating tips
// =====================================
const loadingTips = [
    'Tip: hit Ctrl+Enter to run the editor code',
    'Pure Python, no install, no account',
    'Edit the code on the left and re-run instantly',
    'Try the WebGL demos for shader-driven backgrounds',
    'Open "ImPlot3D: Full Demo" for interactive 3D plots',
    'Once loaded, everything runs locally in your browser',
];

(function setupLoadingBannerExtras() {
    const tipEl = document.getElementById('loading-tip');
    if (tipEl) {
        let i = Math.floor(Math.random() * loadingTips.length);
        tipEl.textContent = loadingTips[i];
        setInterval(() => {
            i = (i + 1) % loadingTips.length;
            tipEl.style.opacity = '0';
            setTimeout(() => {
                tipEl.textContent = loadingTips[i];
                tipEl.style.opacity = '1';
            }, 300);
        }, 4500);
    }

    // Lazily upgrade the video to full preload only after the editor's
    // critical CSS/JS race is over, so it doesn't starve the heavy pyodide
    // downloads (cf. R4 incident). On warm cache pyodide finishes first
    // and the banner hides before this fires — that's fine.
    const vid = document.getElementById('loading-video');
    if (vid) {
        setTimeout(() => {
            vid.preload = 'auto';
            vid.play().catch(() => { /* autoplay may be blocked, ignore */ });
        }, 500);
    }
})();


// =====================================
// Then, initialize everything
// =====================================
async function initialize() {
    await loadPyodideAndPackages();
    await passCanvasToPyodide();
    // Check if a specific demo was requested via ?demo= URL parameter
    const demoFromUrl = getDemoFromUrl();
    if (demoFromUrl) {
        await loadDemoFromUrlIfNeeded();
    } else {
        // Run the initial example automatically
        await runEditorPythonCode();
    }
}

initialize();
