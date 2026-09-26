// js/examples.js

// Initial code in example/_initial_code.py
// ========================================

// load the initial example code
async function initial_example_code() {
    try {
        const response = await fetch('examples/landing_page.py');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const content = await response.text();
        return content; // Return the fetched code
    } catch (error) {
        console.error('Error loading initial code:', error);
        return `# Fallback initial code\nprint("Failed to load initial code.")`;
    }
}

// Check URL for ?demo=filename parameter
function getDemoFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('demo');
}

// Run this function on page load
document.addEventListener('DOMContentLoaded', async () => {
    const initialCode = await initial_example_code();
    editor.setValue(initialCode);
    setLoadedCode(initialCode);
    setEditorLabel('Welcome to Dear ImGui Bundle');
});


// Populate the example selector
// ==============================

// Function to fetch example metadata from JSON
async function fetchExampleMetadata() {
    try {
        const response = await fetch('examples/examples.json');
        const data = await response.json();
        examplesCategories = data.categories || [];
        return data.examples;
    } catch (error) {
        console.error('Error fetching example metadata:', error);
        displayError('Failed to fetch example metadata. See console for details.');
        return [];
    }
}

// Track which packages have already been installed
const installedPackages = new Set();

// Per-package expected install time on a typical 4G connection (ms).
// Used only to tune the asymptotic smoothProgress animation; actual
// install time can be longer or shorter — phase.complete() snaps the
// bar when micropip.install resolves.
const PACKAGE_EXPECTED_MS = {
    'opencv-python': 8000,  // ~11 MB
    'fiatlight':     3000,
};
const PACKAGE_EXPECTED_MS_DEFAULT = 4000;

// Function to install extra packages required by an example
async function installExamplePackages(packages) {
    if (!packages || packages.length === 0) return;
    if (!pyodide) {
        console.error('Pyodide not loaded yet');
        return;
    }
    const toInstall = packages.filter(pkg => !installedPackages.has(pkg));
    if (toInstall.length === 0) return;

    const micropip = pyodide.pyimport("micropip");
    showLoadingModal();
    const total = toInstall.length;
    for (let i = 0; i < total; i++) {
        const pkg = toInstall[i];
        const startPct = (i / total) * 95;
        const endPct   = ((i + 1) / total) * 95;
        const expectedMs = PACKAGE_EXPECTED_MS[pkg] ?? PACKAGE_EXPECTED_MS_DEFAULT;
        const phase = smoothProgress(startPct, endPct, expectedMs,
            (pct) => updateProgress(pct, `Installing ${pkg}…`));
        await micropip.install(pkg);
        phase.complete();
        installedPackages.add(pkg);
        console.log(`${pkg} installed.`);
    }
    updateProgress(100, 'Ready');
    await new Promise(resolve => setTimeout(resolve, 300));
    hideLoadingModal();
}

// Download bundled folders (e.g. fiat_settings) into the Pyodide virtual filesystem
async function installBundleFolders(bundleFolders) {
    if (!bundleFolders || bundleFolders.length === 0 || !pyodide) return;
    for (const folder of bundleFolders) {
        // Fetch the manifest to know which files to download
        const manifestResp = await fetch(`examples/${folder}/manifest.json`);
        if (!manifestResp.ok) {
            console.warn(`No manifest.json found for bundle folder ${folder}`);
            continue;
        }
        const files = await manifestResp.json();

        // Create the folder in Pyodide's virtual FS (relative to cwd: /home/pyodide)
        const targetDir = `/home/pyodide/${folder}`;
        pyodide.runPython(`import os; os.makedirs('${targetDir}', exist_ok=True)`);

        // Download and write each file
        for (const file of files) {
            const resp = await fetch(`examples/${folder}/${file}`);
            if (!resp.ok) continue;
            const content = await resp.text();
            // Write via Python to handle encoding properly
            pyodide.runPython(`
with open('${targetDir}/${file}', 'w') as _f:
    _f.write(${JSON.stringify(content)})
`);
        }
        console.log(`Installed bundle folder: ${folder} (${files.length} files)`);
    }
}

// Function to load example content (and install packages + bundle folders if needed)
async function loadExample(filename, packages, label, bundleFolders) {
    try {
        await installExamplePackages(packages);
        await installBundleFolders(bundleFolders);
        const response = await fetch(`examples/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const content = await response.text();
        editor.setValue(content);
        setLoadedCode(content);
        loadedExampleFilename = filename;
        if (label) setEditorLabel(label);
        clearError(); // Clear previous errors when loading a new example
    } catch (error) {
        console.error('Error loading example:', error);
        displayError('Failed to load the example. Please try again.');
    }
}

// Store example metadata so we can look up packages later
let examplesMetadata = [];
let examplesCategories = [];  // [{name, about}], in the order of the menu
let examplesDocs = {};  // {filename: {title, text}}: examples_docs.json, see ci_scripts/playground_examples_docs.py

// The example loaded in the editor (null for the landing page): runEditorPythonCode() runs it at its own path
let loadedExampleFilename = null;

// The examples menu: the examples by category, and beside the list the title and first paragraph of the hovered one
// (extracted from its docstring)
async function populateExampleSelector() {
    examplesMetadata = await fetchExampleMetadata();
    try {
        examplesDocs = await (await fetch('examples/examples_docs.json')).json();
    } catch (error) {
        console.warn('No examples_docs.json: the menu shows no descriptions', error);
    }

    const list = document.getElementById('examples-list');
    list.innerHTML = '';
    for (const category of examplesCategories) {
        const name = document.createElement('div');
        name.className = 'examples-category-name';
        name.textContent = category.name;
        const about = document.createElement('div');
        about.className = 'examples-category-about';
        about.textContent = category.about;
        list.append(name, about);
        // Only show non-hidden demos in the menu
        for (const example of examplesMetadata) {
            if (example.hidden || example.category !== category.name) continue;
            const item = document.createElement('button');
            item.className = 'examples-item';
            item.textContent = example.label;
            item.dataset.filename = example.filename;
            item.addEventListener('mouseenter', () => showExampleDoc(example.filename));
            item.addEventListener('focus', () => showExampleDoc(example.filename));
            item.addEventListener('click', async () => {
                closeExamplesMenu();
                await loadDemoByFilename(example.filename);
            });
            list.appendChild(item);
        }
    }
}

// The detail pane of the menu: the example's title, first paragraph (markdown, rendered by marked.js) and picture
function showExampleDoc(filename) {
    const detail = document.getElementById('examples-detail');
    detail.innerHTML = '';
    const doc = examplesDocs[filename];
    if (!doc) return;
    const title = document.createElement('div');
    title.className = 'examples-detail-title';
    title.textContent = doc.title;
    const text = document.createElement('div');
    if (typeof marked !== 'undefined') {
        text.innerHTML = marked.parse(doc.text);  // our own docstrings: trusted markdown
        for (const link of text.querySelectorAll('a')) link.target = '_blank';
    } else {
        text.textContent = doc.text;  // marked.js could not be loaded: the markdown as is
    }
    // Its picture, from the website resources (made by ci_scripts/playground_screenshots.py): loaded when hovered
    const picture = document.createElement('img');
    picture.className = 'examples-detail-picture';
    picture.alt = '';
    picture.onerror = () => picture.remove();  // no picture yet, or served without the resources
    picture.src = '../resources/playground/' + filename.split('/').pop().replace(/\.py$/, '.webp');
    detail.append(title, text, picture);
}

// Highlights the example loaded in the editor
function markCurrentExample(filename) {
    for (const item of document.querySelectorAll('.examples-item'))
        item.classList.toggle('current', item.dataset.filename === filename);
}

function openExamplesMenu() {
    document.getElementById('examples-panel').hidden = false;
    document.getElementById('examples-button').setAttribute('aria-expanded', 'true');
    const current = document.querySelector('.examples-item.current');
    showExampleDoc(current ? current.dataset.filename : 'landing_page.py');
    if (current) current.scrollIntoView({block: 'nearest'});
}

function closeExamplesMenu() {
    document.getElementById('examples-panel').hidden = true;
    document.getElementById('examples-button').setAttribute('aria-expanded', 'false');
}

// Load a demo by filename (works for both visible and hidden demos)
async function loadDemoByFilename(filename, updateHistory = true) {
    // Look up in metadata (includes hidden demos)
    const example = examplesMetadata.find(e => e.filename === filename);
    const packages = example ? example.packages : undefined;
    const label = example ? example.label : filename;
    const bundleFolders = example ? example.bundle_folders : undefined;
    await loadExample(filename, packages, label, bundleFolders);
    markCurrentExample(filename);
    // Update browser URL and history
    if (updateHistory) {
        const url = new URL(window.location);
        url.searchParams.set('demo', filename);
        history.pushState({demo: filename}, '', url);
    }
    await runEditorPythonCode();
}

// Check ?demo= URL parameter and load the specified demo after Pyodide is ready
async function loadDemoFromUrlIfNeeded() {
    const demoFile = getDemoFromUrl();
    if (demoFile) {
        // Wait for metadata to be available
        if (examplesMetadata.length === 0) {
            examplesMetadata = await fetchExampleMetadata();
        }
        await loadDemoByFilename(demoFile);
    }
}

// Initialize the examples menu on page load
document.addEventListener('DOMContentLoaded', () => {
    populateExampleSelector().then(() => markCurrentExample(getDemoFromUrl() || 'landing_page.py'));

    const panel = document.getElementById('examples-panel');
    document.getElementById('examples-button').addEventListener('click', () => {
        if (panel.hidden) openExamplesMenu(); else closeExamplesMenu();
    });
    // Closed by a click outside, or Escape (listened in the capture phase: the canvas may stop the events)
    document.addEventListener('pointerdown', (event) => {
        if (!panel.hidden && !document.getElementById('examples-menu').contains(event.target)) closeExamplesMenu();
    }, true);
    document.addEventListener('keydown', (event) => {
        if (!panel.hidden && event.key === 'Escape') closeExamplesMenu();
    }, true);

    // Handle browser back/forward buttons
    window.addEventListener('popstate', async (event) => {
        if (event.state && event.state.demo) {
            await loadDemoByFilename(event.state.demo, false);
        } else {
            // Back to the root URL (no ?demo=): restore the landing page
            const initialCode = await initial_example_code();
            editor.setValue(initialCode);
            setLoadedCode(initialCode);
            loadedExampleFilename = null;
            setEditorLabel('Welcome to Dear ImGui Bundle');
            clearError();
            markCurrentExample('landing_page.py');
            await runEditorPythonCode();
        }
    });
});
