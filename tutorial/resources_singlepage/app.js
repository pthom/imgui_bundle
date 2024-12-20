import { initTOC } from "./toc_loader.js";
import { initResizer } from "./resizer.js";
import { loadPage } from "./page_loader.js";

async function initializeAll() {
    await initTOC();
    initResizer();
    loadPage("discover/hello_world.md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
