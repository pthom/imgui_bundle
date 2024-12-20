import { marked } from "marked";
import { baseUrl } from "marked-base-url";

async function loadToc() {
    const response = await fetch("toc.json");
    const toc = await response.json();
    // Build sidebar navigation from toc
}

async function loadPage(mdPath) {
    console.log("loadPage " + mdPath);

    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);

    marked.use(baseUrl(baseUrlPath));

    // Fetch and parse the Markdown
    const response = await fetch(mdPath);
    const mdText = await response.text();
    const html = marked.parse(mdText);

    // Update the content area
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;

    buildBreadcrumbs();
}
function buildBreadcrumbs() {
    // scan content for h2 headings
}

// Initialize all parts of the app
async function initializeAll() {
    await loadToc();
    initResizer();
    // In the future, initTOC(), initMarkdownLoading(), etc.
    loadPage("discover/hello_world.md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
