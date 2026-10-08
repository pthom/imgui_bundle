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

// The editor folds into a slim rail at the left (the canvas takes the width), and unfolds from it
const CODE_FOLD_DURATION_MS = 250;  // as the width transition of .code-folding in styles.css
function setCodeFolded(folded) {
    const container = document.getElementById('editor-and-canvas-container');
    container.classList.add('code-folding');
    container.classList.toggle('code-hidden', folded);
    // The canvas follows the slide. From a timer, as the splitter from mouse events: a resize clears the canvas, and
    // a timer runs before the frame is drawn (an animation frame callback may run after, and show a black canvas)
    const follow = setInterval(() => window.dispatchEvent(new Event('resize')), 16);
    setTimeout(() => {
        clearInterval(follow);
        window.dispatchEvent(new Event('resize'));
        container.classList.remove('code-folding');  // Split.js drags without a transition
        if (!folded) editor.refresh();  // CodeMirror measures its lines again once visible
    }, CODE_FOLD_DURATION_MS + 50);
}
document.getElementById('code-fold').addEventListener('click', () => setCodeFolded(true));
document.getElementById('code-rail').addEventListener('click', () => setCodeFolded(false));

// A phone (the narrow media query of styles.css) shows one pane at a time, Demo or Code, from the switch in the
// toolbar. The fold is the desktop's: a narrow screen unfolds the code, so that the toolbar shows.
const narrowScreen = window.matchMedia('(max-width: 768px)');
function setPane(pane) {
    document.body.classList.toggle('pane-code', pane === 'code');
    document.body.classList.toggle('pane-demo', pane !== 'code');
    for (const button of document.querySelectorAll('#pane-switch button'))
        button.classList.toggle('active', button.dataset.pane === pane);
    window.dispatchEvent(new Event('resize'));  // the canvas takes the pane's size
    if (pane === 'code') editor.refresh();  // CodeMirror measures its lines again once visible
}
for (const button of document.querySelectorAll('#pane-switch button'))
    button.addEventListener('click', () => setPane(button.dataset.pane));
function onNarrowScreenChange() {
    if (narrowScreen.matches)
        document.getElementById('editor-and-canvas-container').classList.remove('code-hidden');
    window.dispatchEvent(new Event('resize'));
}
narrowScreen.addEventListener('change', onNarrowScreenChange);
setPane('demo');
onNarrowScreenChange();
// The page starts with the code folded (index.html), for the welcome; a link to a demo shows its code from the start
if (getDemoFromUrl())
    document.getElementById('editor-and-canvas-container').classList.remove('code-hidden');

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
    if (narrowScreen.matches) setPane('demo');  // a phone: the result shows
    await runEditorPythonCode();
    _lastRunCode = editor.getValue();
    runButton.classList.remove('needs-run');
});

// Show platform-appropriate shortcut hint
const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
document.getElementById('run-shortcut').textContent = isMac ? '⌘↵' : 'Ctrl+Enter';

// Cmd+F / Ctrl+F in the app (a markdown document's find bar), not the browser's find bar, which would take the focus.
// Only while the canvas has the focus: in the code editor, the browser's find stays.
document.getElementById('canvas').addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && (e.key === 'f' || e.key === 'F')) e.preventDefault();
});

// Keyboard shortcut: Ctrl+Enter (or Cmd+Enter on Mac)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (runButton.disabled) return;  // Pyodide not ready yet
        if (narrowScreen.matches) setPane('demo');
        runEditorPythonCode();
    }
});

// Track modifications: compare editor content to last loaded code
let _lastLoadedCode = '';
let _lastRunCode = '';

function setLoadedCode(code) {
    hideDesktopPanel();
    _lastLoadedCode = code;
    _lastRunCode = code;
    document.getElementById('editor-modified').classList.remove('visible');
    runButton.classList.remove('needs-run');
}

editor.on('change', () => {
    const currentCode = editor.getValue();
    const modifiedFromFile = currentCode !== _lastLoadedCode;
    if (modifiedFromFile) hideDesktopPanel();  // an edit may make a desktop-only demo run here: let the user try
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

// The panel over the canvas for a desktop-only demo (its code is in the editor, it does not run here): its picture,
// the notice, and a chip per variant when it has some (the Python backends: each chip loads its file). The Run
// button is off until the code is edited, or another demo is loaded.
function showDesktopPanel(example, filename = example.filename) {
    const panel = document.getElementById('desktop-panel');
    const picture = document.getElementById('desktop-panel-picture');
    picture.hidden = false;
    picture.onerror = () => { picture.hidden = true; };  // no picture for this demo
    picture.src = '../resources/playground/' + example.filename.split('/').pop().replace(/\.py$/, '.jpg');
    panel.querySelector('a').href = githubUrl(example.source, filename);
    const variants = document.getElementById('desktop-panel-variants');
    variants.innerHTML = '';
    for (const variant of example.variants || []) {
        const chip = element('button', 'gallery-chip' + (variant.filename === filename ? ' current' : ''), variant.label);
        chip.addEventListener('click', async () => {
            await loadExample(variant.filename, example.packages, example.label, example.bundle_folders, example.source);
            showDesktopPanel(example, variant.filename);  // loadExample hid it
        });
        variants.appendChild(chip);
    }
    panel.hidden = false;
    runButton.disabled = true;
}

function hideDesktopPanel() {
    const panel = document.getElementById('desktop-panel');
    if (panel.hidden) return;
    panel.hidden = true;
    runButton.disabled = false;
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
        // Run the welcome (js/examples.js)
        await prepareWelcome();
        await runEditorPythonCode();
    }
}

initialize();
