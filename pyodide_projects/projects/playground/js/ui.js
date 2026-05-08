// js/ui.js

// Function to update the progress bar
function updateProgress(percent, text) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    progressBar.style.width = `${percent}%`;
    progressText.textContent = text;
    console.log(`Progress: ${percent}% - ${text}`);
}

// Show/hide the non-blocking loading banner overlaid on the canvas region.
// While shown, the Run button is disabled (Pyodide isn't ready yet).
function showLoadingModal() {
    const banner = document.getElementById('loading-banner');
    banner.style.display = '';  // Clear any inline display:none
    banner.classList.remove('hidden');
    // Snap the progress bar to 0 without the CSS transition. Otherwise
    // mid-session reopens (extra wheel installs after a previous demo
    // finished at 100%) animate the bar from 100% downward, racing
    // against smoothProgress's climb-up — visually surprising.
    const bar = document.getElementById('progress-bar');
    if (bar) {
        const prev = bar.style.transition;
        bar.style.transition = 'none';
        bar.style.width = '0%';
        // Force reflow so the no-transition write is committed before we restore.
        void bar.offsetHeight;
        bar.style.transition = prev;
    }
    const runBtn = document.getElementById('run-button');
    if (runBtn) runBtn.disabled = true;
}

function hideLoadingModal() {
    const banner = document.getElementById('loading-banner');
    banner.style.display = 'none';
    const runBtn = document.getElementById('run-button');
    if (runBtn) runBtn.disabled = false;
}

// Function to display errors in the error window
function displayError(message) {
    console.log('Displaying error:', message); // Debug log
    const errorOutput = document.getElementById('error-output').querySelector('pre');
    errorOutput.textContent = message; // Use textContent for plain text
    document.getElementById('error-output').classList.remove('hidden');
}

// Function to clear the error window
function clearError() {
    const errorOutput = document.getElementById('error-output').querySelector('pre');
    errorOutput.textContent = '';
    document.getElementById('error-output').classList.add('hidden');
}

// Function to close the error window
function closeErrorWindow() {
    console.log('Closing error window');
    const errorOutput = document.getElementById('error-output');
    errorOutput.classList.add('hidden');
    const pre = errorOutput.querySelector('pre');
    pre.textContent = '';
}

// Add event listener for the close button
document.addEventListener('DOMContentLoaded', () => {
    const closeErrorBtn = document.getElementById('close-error');
    if (closeErrorBtn) {
        closeErrorBtn.addEventListener('click', closeErrorWindow);
    }
});
