// app.js (just an outline)
async function loadToc() {
    const response = await fetch("toc.json");
    const toc = await response.json();
    // Build sidebar navigation from toc
}

async function loadPage(mdPath) {
    const response = await fetch(mdPath);
    const mdText = await response.text();
    const html = marked.parse(mdText);
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;
    buildBreadcrumbs();
}

function buildBreadcrumbs() {
    // scan content for h2 headings
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadToc();
    // load default page
    loadPage("discover/hello_world.md");
});
