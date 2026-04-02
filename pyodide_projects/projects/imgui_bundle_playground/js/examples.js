// js/examples.js

// Initial code in example/_initial_code.py
// ========================================

// load the initial example code
async function initial_example_code() {
    try {
        const response = await fetch('examples/00_landing_page.py');
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
        return data.examples;
    } catch (error) {
        console.error('Error fetching example metadata:', error);
        displayError('Failed to fetch example metadata. See console for details.');
        return [];
    }
}

// Track which packages have already been installed
const installedPackages = new Set();

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
        const percent = Math.round(((i) / total) * 100);
        updateProgress(percent, `Installing ${pkg}...`);
        await micropip.install(pkg);
        installedPackages.add(pkg);
        console.log(`${pkg} installed.`);
    }
    updateProgress(100, 'All packages installed.');
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
        if (label) setEditorLabel(label);
        clearError(); // Clear previous errors when loading a new example
    } catch (error) {
        console.error('Error loading example:', error);
        displayError('Failed to load the example. Please try again.');
    }
}

// Store example metadata so we can look up packages later
let examplesMetadata = [];

// Function to populate example selector
async function populateExampleSelector() {
    examplesMetadata = await fetchExampleMetadata();

    const exampleSelector = document.getElementById('example-selector');
    exampleSelector.innerHTML = '';
    // Only show non-hidden demos in the dropdown
    examplesMetadata.forEach((example, index) => {
        if (example.hidden) return;
        const option = document.createElement('option');
        option.value = example.filename;
        option.textContent = example.label;
        exampleSelector.appendChild(option);
    });
}

// Load a demo by filename (works for both visible and hidden demos)
async function loadDemoByFilename(filename, updateHistory = true) {
    // Look up in metadata (includes hidden demos)
    const example = examplesMetadata.find(e => e.filename === filename);
    const packages = example ? example.packages : undefined;
    const label = example ? example.label : filename;
    const bundleFolders = example ? example.bundle_folders : undefined;
    await loadExample(filename, packages, label, bundleFolders);
    // Set the dropdown to match (if the demo is visible)
    const selector = document.getElementById('example-selector');
    if (selector) {
        const option = Array.from(selector.options).find(o => o.value === filename);
        if (option) selector.value = filename;
    }
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

// Initialize the example selector on page load
document.addEventListener('DOMContentLoaded', () => {
    populateExampleSelector();

    // Add event listener for example selector changes
    const exampleSelectorElement = document.getElementById('example-selector');

    exampleSelectorElement.addEventListener('change', async (event) => {
        const selectedFilename = event.target.value;
        if (selectedFilename) {
            await loadDemoByFilename(selectedFilename);
        }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', async (event) => {
        if (event.state && event.state.demo) {
            await loadDemoByFilename(event.state.demo, false);
        }
    });
});
