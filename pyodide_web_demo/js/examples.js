// js/examples.js

function initial_example_code() {
    code = `# Write your Python code here
from imgui_bundle import immapp, imgui_md

immapp.run(lambda: imgui_md.render("# Hello, Pyodide!"), with_markdown=True)
    `
    return code;
}

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

// Function to load example content
async function loadExample(filename) {
    try {
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

// Function to populate example selector
async function populateExampleSelector() {
    const examplesList = await fetchExampleMetadata();

    const exampleSelector = document.getElementById('example-selector');
    exampleSelector.innerHTML = '<option value="">-- Select an Example --</option>';
    examplesList.forEach((example, index) => {
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

    exampleSelectorElement.addEventListener('change', (event) => {
        const selectedFilename = event.target.value;
        if (selectedFilename) {
            loadExample(selectedFilename);
        }
    });
});
