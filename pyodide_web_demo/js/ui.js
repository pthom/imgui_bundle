// js/ui.js

// Function to update the progress bar
function updateProgress(percent, text) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    progressBar.style.width = `${percent}%`;
    progressText.textContent = text;
    console.log(`Progress: ${percent}% - ${text}`);
}

// Function to show the loading modal
function showLoadingModal() {
    console.log('Showing loading modal');
    const loadingModal = document.getElementById('loading-modal');
    loadingModal.classList.remove('hidden');
}

// Function to hide the loading modal
function hideLoadingModal() {
    // console.log('Hiding loading modal');
    const loadingModal = document.getElementById('loading-modal');
    loadingModal.style.display = 'none';
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
