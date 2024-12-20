import { initTOC, tocRoot } from "./toc_loader.js";
import { initResizer } from "./resizer.js";
import { loadPage } from "./page_loader.js";

async function initializeAll() {
    await initTOC();
    initResizer();

    const rootPage = tocRoot()
    loadPage(rootPage.file + ".md");
    // loadPage("discover/hello_world.md")
}

document.addEventListener("DOMContentLoaded", initializeAll);
