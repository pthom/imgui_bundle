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

// Run this function on page load
document.addEventListener('DOMContentLoaded', async () => {
    const initialCode = await initial_example_code();
    editor.setValue(initialCode); // Set the editor's value to the loaded code
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

// Function to load example content (and install packages if needed)
async function loadExample(filename, packages) {
    try {
        await installExamplePackages(packages);
        const response = await fetch(`examples/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const content = await response.text();
        editor.setValue(content);
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
    exampleSelector.innerHTML = '<option value="">-- Select an Example --</option>';
    examplesMetadata.forEach((example, index) => {
        const option = document.createElement('option');
        option.value = example.filename;
        option.textContent = example.label;
        exampleSelector.appendChild(option);
    });
}

// Initialize the example selector on page load
document.addEventListener('DOMContentLoaded', () => {
    populateExampleSelector();

    // Add event listener for example selector changes
    const exampleSelectorElement = document.getElementById('example-selector');

    const runBtn = document.getElementById('run-button');

    exampleSelectorElement.addEventListener('change', (event) => {
        const selectedFilename = event.target.value;
        if (selectedFilename) {
            const example = examplesMetadata.find(e => e.filename === selectedFilename);
            loadExample(selectedFilename, example ? example.packages : undefined);
            // Gently flash the Run button until clicked
            runBtn.classList.add('flashing');
        }
    });

    runBtn.addEventListener('click', () => {
        runBtn.classList.remove('flashing');
    });
});
